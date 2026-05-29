from django.shortcuts import render
from django.http import JsonResponse
from .models import Listing, Reservation
from datetime import datetime, timedelta
from django.db.models import Count

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