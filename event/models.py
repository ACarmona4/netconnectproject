from django.db import models
from company.models import Company

# Create your models here.
class Event(models.Model):
    id = models.AutoField(primary_key=True)
    picture = models.ImageField(upload_to='event/images/', default='event/images/default.jpg')
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    organizer = models.CharField(max_length=100)
    participants = models.ManyToManyField(Company, blank=True)
    
    def __str__(self):
        return (f'{self.name} - {self.date}')
