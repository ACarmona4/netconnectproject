from django.db import models

# Create your models here.
class event(models.Model):
    picture = models.ImageField(upload_to='event/images/', default='event/images/default.jpg')
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    organizer = models.CharField(max_length=100)
    
    def __str__(self):
        return (f'{self.name} - {self.date}')
