import os
import base64
from .models import Event
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
            event.attendees.add(request.user)
            messages.success(request, f'Te has inscrito exitosamente al evento {event.name}')
            user_email = request.user.email
            evento_confirmacion(request, user_email, event_id)
        else:
            messages.warning(request, f'Ya estás inscrito en el evento {event.name}')
    else:
        messages.error(request, 'Debes iniciar sesión para inscribirte en un evento.')
    
    return redirect('events') 

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

@login_required
def my_events(request):
    current_time = timezone.now()
    
    future_events = Event.objects.filter(attendees=request.user, date__gte=current_time).order_by('date')
    past_events = Event.objects.filter(attendees=request.user, date__lt=current_time).order_by('-date')
    
    return render(request, 'my_events.html', {
        'future_events': future_events,
        'past_events': past_events
    })
    

load_dotenv()
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_PATH')
TOKEN_FILE = os.getenv('GOOGLE_TOKEN_PATH')
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)  
        with open(TOKEN_FILE, 'w') as token_file:
            token_file.write(creds.to_json())
    return creds

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

def evento_confirmacion(request, user_email, event_id):
    event = Event.objects.get(id=event_id)
    subject = f"Confirmación de inscripción al evento: {event.name}"
    
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
