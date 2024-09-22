from django.shortcuts import render
from django.http import JsonResponse
from .models import Event
from django.utils import timezone

# Create your views here.
def home(request):
    return render(request, 'home.html')

def displayEvents(request):
    current_time = timezone.now()
    events = Event.objects.filter(date__gte=current_time).order_by('date')[:4]
    
    return render(request, 'events.html', {'events': events})