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
    location = models.CharField(max_length=100)
    organizer = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='organized_events')
    participants = models.ManyToManyField(Company, blank=True, related_name='participated_events')
    attendees = models.ManyToManyField(User, blank=True, related_name='events_attending') 
    
    def __str__(self):
        return (f'{self.name} - {self.date}')