from django.contrib import admin
from .models import Event, AdvertiserRequest

class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location']
    filter_horizontal = ('participants',)  
    filter_horizontal = ('attendees',)
admin.site.register(Event, EventAdmin)


@admin.register(AdvertiserRequest)
class AdvertiserRequestAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_name', 'contact_email', 'event', 'status')
    list_filter = ('status', 'event')
    search_fields = ('company_name', 'contact_name', 'contact_email')
