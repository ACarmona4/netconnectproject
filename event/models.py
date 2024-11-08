from django.db import models
from company.models import Company
from accounts.models import User  
import qrcode
from io import BytesIO
from django.core.files import File

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    picture = models.ImageField(upload_to='event/images/', default='event/images/default.jpg')
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    date = models.DateField()
    time = models.TimeField()
    time_finish = models.TimeField(default='23:59:59')
    location = models.CharField(max_length=100)
    organizer = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='organized_events')
    participants = models.ManyToManyField(Company, blank=True, related_name='participated_events')
    attendees = models.ManyToManyField(User, blank=True, related_name='events_attending') 

    def __str__(self):
        return f'{self.name} - {self.date}'


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendances")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendances")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    attended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.event.name}"

    def save(self, *args, **kwargs):
        if not self.qr_code:
            qr = qrcode.make(f"{self.user.id}-{self.event.id}")
            qr_io = BytesIO()
            qr.save(qr_io, 'PNG')
            qr_file = File(qr_io, name=f"qr_{self.user.id}_{self.event.id}.png")
            self.qr_code = qr_file
        super().save(*args, **kwargs)


class AdvertiserRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
    ]

    company_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    message = models.TextField()
    description = models.TextField()
    logo = models.ImageField(upload_to='company/images/')  
    event = models.ForeignKey('Event', on_delete=models.CASCADE)  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  

    def __str__(self):
        return f"{self.company_name} - {self.event.name}"