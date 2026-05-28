from django.shortcuts import render
from django.http import JsonResponse
from .models import Listing, Reservation
from datetime import datetime

def calendar_view(request):
    listings = Listing.objects.all()
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    return render(request, 'reservations/calendar.html', {
        'listings': listings,
        'year': year,
        'month': month,
    })

def get_reservations(request):
    listing_id = request.GET.get('listing_id')
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    # Filter by listing
    if listing_id and listing_id != 'all':
        reservations = Reservation.objects.filter(listing_id=listing_id)
    else:
        reservations = Reservation.objects.all()
    
    # Get first and last day of month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year+1, 1, 1).date()
    else:
        end_date = datetime(year, month+1, 1).date()
    
    # Filter reservations that overlap this month
    reservations = reservations.filter(
        checkin_date__lt=end_date,
        checkout_date__gte=start_date
    )
    
    data = []
    for res in reservations:
        data.append({
            'id': res.id,
            'guest_name': res.guest_name,
            'guest_photo': res.guest_photo.url if res.guest_photo else '',
            'checkin': res.checkin_date.strftime('%Y-%m-%d'),
            'checkout': res.checkout_date.strftime('%Y-%m-%d'),
        })
    
    return JsonResponse(data, safe=False)