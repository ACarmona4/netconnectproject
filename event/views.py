import os
import base64
from datetime import datetime, timedelta
from .models import Event, AdvertiserRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from .forms import EventForm
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
from .forms import AdvertiseForm

# Cargar variables de entorno
load_dotenv()
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH')
TOKEN_FILE = os.getenv('GOOGLE_TOKEN_PATH')

# Página de inicio
def home(request):
    return render(request, 'home.html')

# Mostrar eventos
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

# Detalles de evento
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Obtener los nombres de las empresas en el modelo `Company` que participan en el evento
    participant_names = list(event.participants.values_list('name', flat=True))
    
    # Obtener las solicitudes aceptadas en `AdvertiserRequest`
    accepted_requests = AdvertiserRequest.objects.filter(event=event, status='accepted')
    accepted_request_names = list(accepted_requests.values_list('company_name', flat=True))
    
    # Combina ambas listas para tener todas las empresas participantes
    all_participant_names = participant_names + accepted_request_names

    return render(request, 'event_detail.html', {
        'event': event,
        'accepted_requests': accepted_requests,
        'all_participant_names': all_participant_names,
    })
def manageEvent(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user.company)
    advertiser_requests = AdvertiserRequest.objects.filter(event=event, status='pending')
    attendees = event.attendees.all()
    # Obtén las empresas participantes que ya están en el modelo `Company`
    registered_companies = event.participants.all()

    # Obtén las solicitudes aceptadas en `AdvertiserRequest`
    accepted_requests = AdvertiserRequest.objects.filter(event=event, status='accepted')

    return render(request, 'manage_event.html', {
        'event': event,
        'advertiser_requests': advertiser_requests,
        'attendees': attendees,
        'registered_companies': registered_companies,
        'accepted_requests': accepted_requests,
    })
# Inscribirse a un evento
@login_required
def subscribe_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.user not in event.attendees.all():
        event.attendees.add(request.user)
        messages.success(request, f'Te has inscrito exitosamente al evento {event.name}')
        user_email = request.user.email
        evento_confirmacion(request, user_email, event_id)
    else:
        messages.warning(request, f'Ya estás inscrito en el evento {event.name}')
    
    return redirect('my_events')

#Desinscribirse de un evento
@login_required
def unsubscribe_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user in event.attendees.all():
        event.attendees.remove(request.user)
        messages.success(request, f'¡Hemos anulado la inscripción! Ya no estás inscrito a {event.name}')
        user_email = request.user.email
        evento_desconfirmacion(request, user_email, event_id)
    else:
        messages.warning(request, 'No estás inscrito en este evento.')

    return redirect('my_events')


def advertise_form(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    existing_company = None

    if request.user.is_authenticated and hasattr(request.user, 'company'):
        # Si el usuario tiene un perfil de empresa asociado, usa sus datos
        existing_company = request.user.company

    if request.method == 'POST':
        form = AdvertiseForm(request.POST, request.FILES, existing_company=existing_company)
        if form.is_valid():
            advertiser_request = form.save(commit=False)
            advertiser_request.event = event  # Asigna el evento

            # Si la empresa ya existe, rellena los datos automáticamente
            if existing_company:
                advertiser_request.company_name = existing_company.name
                advertiser_request.contact_name = existing_company.personInCharge
                advertiser_request.contact_email = existing_company.email
                advertiser_request.logo = existing_company.logo
                advertiser_request.description = existing_company.description
            
            advertiser_request.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = AdvertiseForm(existing_company=existing_company)

    return render(request, 'advertise_form.html', {'form': form, 'event': event})

# Ver eventos en los que el usuario está inscrito
@login_required
def my_events(request):
    current_time = timezone.now()
    
    future_events = Event.objects.filter(attendees=request.user, date__gte=current_time).order_by('date')
    past_events = Event.objects.filter(attendees=request.user, date__lt=current_time).order_by('-date')
    
    return render(request, 'my_events.html', {
        'future_events': future_events,
        'past_events': past_events
    })

# Añadir un evento al Google Calendar del usuario
@login_required
def add_event_to_google_calendar(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    SCOPES = ['https://www.googleapis.com/auth/calendar.events']

    user_token_file = f'tokens/token_{request.user.id}.json'
    
    creds = None
    if os.path.exists(user_token_file):
        creds = Credentials.from_authorized_user_file(user_token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        os.makedirs(os.path.dirname(user_token_file), exist_ok=True)
        with open(user_token_file, 'w') as token_file:
            token_file.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)
    event_data = {
        'summary': event.name,
        'location': event.location,
        'description': f"Organizado por {event.organizer.name}",
        'start': {
            'dateTime': datetime.combine(event.date, event.time).isoformat(),
            'timeZone': 'America/Bogota',
        },
        'end': {
            'dateTime': datetime.combine(event.date, event.time_finish).isoformat(),
            'timeZone': 'America/Bogota',
        },
    }

    try:
        created_event = service.events().insert(calendarId='primary', body=event_data).execute()
        messages.success(request, f"El evento {event.name} ha sido añadido a tu Google Calendar.")
        return redirect('my_events')
    except Exception as e:
        messages.error(request, f"No se pudo añadir el evento al calendario: {e}")
        return redirect('my_events')
    
# Autenticación de Gmail
SCOPES_GMAIL = ['https://www.googleapis.com/auth/gmail.send']

def gmail_authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES_GMAIL)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES_GMAIL)
            creds = flow.run_local_server(port=8080)
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)  
        with open(TOKEN_FILE, 'w') as token_file:
            token_file.write(creds.to_json())
    return creds

# Enviar correo electrónico
def send_email(user_email, subject, message):
    creds = gmail_authenticate()
    service = build('gmail', 'v1', credentials=creds)
    
    message_mime = MIMEText(message, "html") 
    message_mime['to'] = user_email
    message_mime['subject'] = subject
    raw = base64.urlsafe_b64encode(message_mime.as_bytes()).decode()

    message = {'raw': raw}
    try:
        message = service.users().messages().send(userId="me", body=message).execute()
        return HttpResponse('Correo enviado correctamente')
    except Exception as e:
        return HttpResponse(f'Error enviando el correo: {str(e)}')

# Funciones de confirmación y desconfirmación de eventos por correo
def evento_confirmacion(request, user_email, event_id):
    event = Event.objects.get(id=event_id)
    subject = f"Confirmación de inscripción al evento {event.name}"
    
    message = f"""
    <html>
        <body>
            <h2>Confirmación de Inscripción al Evento</h2>
            <p>Estimado {request.user.name},</p>
            <p>¡Gracias por inscribirte al evento <strong>{event.name}</strong>!</p>
            <p><strong>Detalles del evento:</strong></p>
            <ul>
                <li><strong>Fecha:</strong> {event.date}</li>
                <li><strong>Hora:</strong> {event.time}</li>
                <li><strong>Ubicación:</strong> {event.location}</li>
                <li><strong>Organizador:</strong> {event.organizer.name}</li>
            </ul>
            <p>Esperamos contar con tu presencia y que disfrutes de esta experiencia.</p>
            <p>Atentamente,</p>
            <p>El equipo de NetConnect</p>
        </body>
    </html>
    """
    
    return send_email(user_email, subject, message)

def evento_desconfirmacion(request, user_email, event_id):
    event = Event.objects.get(id=event_id)
    subject = f"Anulación de inscripción al evento {event.name}"
    
    message = f"""
    <html>
        <body>
            <h2>Anulación de Inscripción al Evento</h2>
            <p>Estimado {request.user.name},</p>
            <p>¡Hemos anulado tu inscripción al evento <strong>{event.name}</strong>!</p>
            <p>Esperamos contar con tu presencia en futuros eventos.</p>
            <p>Atentamente,</p>
            <p>El equipo de NetConnect</p>
        </body>
    </html>
    """
    
    return send_email(user_email, subject, message)