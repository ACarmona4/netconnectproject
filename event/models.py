from django.db import models
from company.models import Company
from accounts.models import User  

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
        return (f'{self.name} - {self.date}')
    

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
    event = models.ForeignKey('Event', on_delete=models.CASCADE)  # Relaciona con el evento
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Estado de la solicitud

    def __str__(self):
        return f"{self.company_name} - {self.event.name}"
    


        