from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Event
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
            Q(organizer__icontains=searchTerm)
        )

    return render(request, 'events.html', {
        'searchTerm': searchTerm,
        'carousel_events': carousel_events,  
        'events': events 
    })
    
def companyDashboard(request):
    if request.user.is_company:
        if request.method == 'POST':
            form = EventForm(request.POST, request.FILES)
            if form.is_valid():
                event = form.save(commit=False)
                event.organizer = request.user.company.name
                event.save()
                messages.success(request, '¡Evento creado con éxito!')
                return redirect('events')
        else:
            form = EventForm()
        
        #Funcionalidades futuras
        asistentes = [] 
        return render(request, 'companies.html', {'form': form, 'asistentes': asistentes})
    
    else:
        messages.error(request, 'Solo las empresas pueden acceder a este panel.')
        return redirect('events')
