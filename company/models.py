from django.db import models

# Create your models here.
class Company(models.Model):
    id = models.AutoField(primary_key=True)
    logo = models.ImageField(upload_to='company/images/', default='company/images/default.jpg')
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    email = models.EmailField()
    personInCharge = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
