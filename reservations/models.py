from django.db import models

class Listing(models.Model):
    room_title = models.CharField(max_length=255)
    room_image = models.ImageField(upload_to='rooms/')
    
    def __str__(self):
        return self.room_title

class Reservation(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reservations')
    guest_name = models.CharField(max_length=255)
    guest_photo = models.ImageField(upload_to='guests/')
    checkin_date = models.DateField()
    checkout_date = models.DateField()
    
    def __str__(self):
        return f"{self.guest_name} - {self.listing.room_title}"