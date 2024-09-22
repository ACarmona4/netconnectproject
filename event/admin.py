from django.contrib import admin
from .models import Event

class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location']
    filter_horizontal = ('participants',)  

admin.site.register(Event, EventAdmin)
