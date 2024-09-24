from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Event
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from .forms import EventForm

# Create your views here.
def home(request):
    return render(request, 'home.html')

def displayEvents(request):
    current_time = timezone.now()

    carousel_events = Event.objects.filter(date__gte=current_time).order_by('date')[:4]
    events = Event.objects.filter(date__gte=current_time).order_by('date')
    
    searchTerm = request.GET.get('Encuentra un evento')
    if searchTerm:
        events = events.filter(
            Q(name__icontains=searchTerm) | 
            Q(location__icontains=searchTerm) | 
            Q(organizer__name__icontains=searchTerm)  
        )

    return render(request, 'events.html', {
        'searchTerm': searchTerm,
        'carousel_events': carousel_events,  
        'events': events 
    })

@login_required
def subscribe_event(request, event_id):
    if request.user.is_authenticated and not request.user.is_company:
        event = get_object_or_404(Event, id=event_id)
        
        if request.user not in event.attendees.all():
            event.attendees.add(request.user)  # Añade al usuario a los asistentes de ese evento
            messages.success(request, f'Te has inscrito exitosamente al evento: {event.name}')
        else:
            messages.warning(request, f'Ya estás inscrito en el evento: {event.name}')
    else:
        messages.error(request, 'Debes iniciar sesión para inscribirte en un evento.')
    
    return redirect('events')  # Redirige a la página de eventos

from django.shortcuts import render
from event.models import Event
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def my_events(request):
    current_time = timezone.now()
    
    # Filtrar eventos futuros y pasados a los que el usuario está inscrito
    future_events = Event.objects.filter(attendees=request.user, date__gte=current_time).order_by('date')
    past_events = Event.objects.filter(attendees=request.user, date__lt=current_time).order_by('-date')
    
    return render(request, 'my_events.html', {
        'future_events': future_events,
        'past_events': past_events
    })
