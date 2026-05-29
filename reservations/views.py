from django.shortcuts import render
from django.http import JsonResponse
from .models import Listing, Reservation
from datetime import datetime, timedelta
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt

def calendar_view(request):
    listings = Listing.objects.all()
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    return render(request, 'reservations/calendar.html', {
        'listings': listings,
        'year': year,
        'month': month,
    })

def dashboard_view(request):
    """Dashboard showing all reservations across all rooms"""
    listings = Listing.objects.all()
    today = datetime.now().date()
    
    # Get reservations for the current month
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year+1, 1, 1).date()
    else:
        end_date = datetime(year, month+1, 1).date()
    
    reservations = Reservation.objects.filter(
        checkin_date__lt=end_date,
        checkout_date__gte=start_date
    ).select_related('listing')
    
    return render(request, 'reservations/dashboard.html', {
        'listings': listings,
        'reservations': reservations,
        'year': year,
        'month': month,
        'today': today,
    })

def get_dashboard_data(request):
    """API endpoint for dashboard data"""
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year+1, 1, 1).date()
    else:
        end_date = datetime(year, month+1, 1).date()
    
    reservations = Reservation.objects.filter(
        checkin_date__lt=end_date,
        checkout_date__gte=start_date
    ).select_related('listing')
    
    # Group by date
    data = {}
    for res in reservations:
        current_date = res.checkin_date
        while current_date < res.checkout_date and current_date < end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            if date_key not in data:
                data[date_key] = []
            data[date_key].append({
                'id': res.id,
                'guest_name': res.guest_name,
                'guest_photo': res.guest_photo.url if res.guest_photo else '',
                'room_title': res.listing.room_title,
                'checkin': res.checkin_date.strftime('%Y-%m-%d'),
                'checkout': res.checkout_date.strftime('%Y-%m-%d'),
                'room_id': res.listing.id,
            })
            current_date += timedelta(days=1)
    
    return JsonResponse(data)

def get_reservations(request):
    """Existing API endpoint for calendar"""
    listing_id = request.GET.get('listing_id')
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    if listing_id and listing_id != 'all':
        reservations = Reservation.objects.filter(listing_id=listing_id)
    else:
        reservations = Reservation.objects.all()
    
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year+1, 1, 1).date()
    else:
        end_date = datetime(year, month+1, 1).date()
    
    reservations = reservations.filter(
        checkin_date__lt=end_date,
        checkout_date__gte=start_date
    ).select_related('listing')
    
    data = []
    for res in reservations:
        data.append({
            'id': res.id,
            'guest_name': res.guest_name,
            'guest_photo': res.guest_photo.url if res.guest_photo else '',
            'listing_id': res.listing.id,
            'room_title': res.listing.room_title,
            'checkin': res.checkin_date.strftime('%Y-%m-%d'),
            'checkout': res.checkout_date.strftime('%Y-%m-%d'),
        })
    
    return JsonResponse(data, safe=False)


@csrf_exempt
def create_listing(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    title = request.POST.get('room_title')
    if not title:
        return JsonResponse({'error': 'Room title is required'}, status=400)
    image = request.FILES.get('room_image')
    listing = Listing.objects.create(room_title=title, room_image=image)
    return JsonResponse({
        'id': listing.id,
        'room_title': listing.room_title,
        'room_image': listing.room_image.url if listing.room_image else '',
    })


@csrf_exempt
def create_reservation(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    listing_id = request.POST.get('listing_id')
    guest_name = request.POST.get('guest_name')
    guest_photo = request.FILES.get('guest_photo')
    checkin_date = request.POST.get('checkin_date')
    checkout_date = request.POST.get('checkout_date')
    if not all([listing_id, guest_name, checkin_date, checkout_date]):
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        return JsonResponse({'error': 'Listing not found'}, status=404)
    reservation = Reservation.objects.create(
        listing=listing,
        guest_name=guest_name,
        guest_photo=guest_photo,
        checkin_date=checkin_date,
        checkout_date=checkout_date,
    )
    return JsonResponse({
        'id': reservation.id,
        'guest_name': reservation.guest_name,
        'guest_photo': reservation.guest_photo.url if reservation.guest_photo else '',
        'listing_id': listing.id,
        'room_title': listing.room_title,
        'checkin': reservation.checkin_date.strftime('%Y-%m-%d'),
        'checkout': reservation.checkout_date.strftime('%Y-%m-%d'),
    })