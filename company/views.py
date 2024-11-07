from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from event.models import Event, AdvertiserRequest
from event.forms import EventForm
from django.utils import timezone

def companyDashboard(request):
    if request.user.is_authenticated and request.user.is_company:
        # Obtener eventos organizados por la empresa
        company_events = Event.objects.filter(organizer=request.user.company)
        
        # Obtener eventos en los que la empresa participa
        now = timezone.now().date()
        participated_events = Event.objects.filter(participants=request.user.company)

        # Dividir eventos en futuros y pasados
        future_events = participated_events.filter(date__gte=now)
        past_events = participated_events.filter(date__lt=now)
        #Crear Evento

        if request.method == 'POST' and 'create_event' in request.POST:
            form = EventForm(request.POST, request.FILES)
            if form.is_valid():
                event = form.save(commit=False)
                event.organizer = request.user.company
                event.save()
                form.save_m2m()  
                messages.success(request, '¡Evento creado con éxito!')
                return redirect('companies')
        else:
            form = EventForm()

        return render(request, 'companies.html', {
            'company_events': company_events,
            'future_events': future_events,
            'past_events': past_events,
            'form': form
        })
    else:
        # Redirige si el usuario no es una empresa o no está autenticado
        return redirect('login')

    
def update_advertiser_request(request, request_id, action):
    advertiser_request = get_object_or_404(AdvertiserRequest, id=request_id, event__organizer=request.user.company)
    if action == 'accept':
        advertiser_request.status = 'accepted'
        advertiser_request.save()
        # Agrega la empresa a los participantes del evento
        messages.success(request, f'¡Solicitud de {advertiser_request.company_name} aceptada!')
    elif action == 'reject':
        advertiser_request.status = 'rejected'
        advertiser_request.save()
        messages.success(request, f'Solicitud de {advertiser_request.company_name} rechazada.')
    return redirect('companies')

def eventDetails(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user.company)
    advertiser_requests = AdvertiserRequest.objects.filter(event=event, status='pending')
    attendees = event.attendees.all()

    return render(request, 'event_admindetails.html', {
        'event': event,
        'advertiser_requests': advertiser_requests,
        'attendees': attendees,
    })