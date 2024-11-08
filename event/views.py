import os
import base64
import qrcode
from io import BytesIO
from django.urls import reverse
from django.conf import settings
from datetime import datetime, timedelta
from .models import Event, Attendance, AdvertiserRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from .forms import EventForm, AdvertiseForm
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.core.files.base import ContentFile
from dotenv import load_dotenv

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

# Detalles de evento (Perfil del evento)
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participant_names = list(event.participants.values_list('name', flat=True))
    accepted_requests = AdvertiserRequest.objects.filter(event=event, status='accepted')
    accepted_request_names = list(accepted_requests.values_list('company_name', flat=True))
    all_participant_names = participant_names + accepted_request_names

    return render(request, 'event_detail.html', {
        'event': event,
        'accepted_requests': accepted_requests,
        'all_participant_names': all_participant_names,
    })
    
# Detalles del evento (Panel de empresas)
def manageEvent(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user.company)
    advertiser_requests = AdvertiserRequest.objects.filter(event=event, status='pending')
    registered_companies = event.participants.all()
    accepted_requests = AdvertiserRequest.objects.filter(event=event, status='accepted')
    
    attendees = event.attendees.all()
    
    verified_attendees = Attendance.objects.filter(event=event, attended=True).select_related('user')

    return render(request, 'manage_event.html', {
        'event': event,
        'advertiser_requests': advertiser_requests,
        'attendees': attendees, 
        'verified_attendees': verified_attendees,  
        'registered_companies': registered_companies,
        'accepted_requests': accepted_requests,
    })
    
# Eliminar evento
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'El evento ha sido eliminado con éxito.')
        return redirect('companies')  

    return redirect('manage_event', event_id=event.id)  

# Generar QR del evento
def generate_event_qr(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registration_url = request.build_absolute_uri(f"{reverse('register')}?next_event={event.id}")

    qr = qrcode.make(registration_url)
    qr_io = BytesIO()
    qr.save(qr_io, 'PNG')
    qr_io.seek(0)

    response = HttpResponse(qr_io, content_type="image/png")
    response['Content-Disposition'] = f'inline; filename=qr_event_{event.id}.png'
    return response
    
# Inscribirse a un evento
@login_required
def subscribe_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.user not in event.attendees.all():
        event.attendees.add(request.user)
        messages.success(request, f'Te has inscrito exitosamente al evento {event.name}')

        qr_url = request.build_absolute_uri(reverse('verify_qr_code', args=[request.user.id, event.id]))
        qr = qrcode.make(qr_url)
        qr_io = BytesIO()
        qr.save(qr_io, 'PNG')
        
        attendance = Attendance.objects.create(user=request.user, event=event)
        attendance.qr_code.save(f"qr_{request.user.id}_{event.id}.png", ContentFile(qr_io.getvalue()))
        
        user_email = request.user.email
        evento_confirmacion(request, user_email, event_id)
    else:
        messages.warning(request, f'Ya estás inscrito en el evento {event.name}')
    
    return redirect('my_events')

# Verificar QR
def verify_qr_code(request, user_id, event_id):
    try:
        attendance = Attendance.objects.get(user__id=user_id, event__id=event_id)
        if not attendance.attended:
            attendance.attended = True
            attendance.save()
            messages.success(request, f"Asistencia verificada para el evento {attendance.event.name}")
        else:
            messages.warning(request, f"La asistencia para el evento {attendance.event.name} ya ha sido verificada.")

        return render(request, 'verification.html', {
            'user': attendance.user,
        })
    except Attendance.DoesNotExist:
        return HttpResponse("Código QR no válido o asistencia no encontrada.", status=404)

# Ver QR
@login_required
def view_qr_code(request, event_id, user_id):
    attendance = get_object_or_404(Attendance, user_id=user_id, event_id=event_id)
    qr_code = attendance.qr_code

    if qr_code:
        response = HttpResponse(qr_code, content_type="image/png")
        response['Content-Disposition'] = f'inline; filename=qr_{user_id}_{event_id}.png'
        return response
    else:
        return HttpResponse("QR Code no disponible", status=404)
    
#Desinscribirse de un evento
@login_required
def unsubscribe_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user in event.attendees.all():
        event.attendees.remove(request.user)
        Attendance.objects.filter(user=request.user, event=event).delete()
        messages.success(request, f'¡Hemos anulado la inscripción! Ya no estás inscrito a {event.name}')
        user_email = request.user.email
        evento_desconfirmacion(request, user_email, event_id)
    else:
        messages.warning(request, 'No estás inscrito en este evento.')

    return redirect('my_events')

#Postularse como anunciante
def advertise_form(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    existing_company = None

    if request.user.is_authenticated and hasattr(request.user, 'company'):
        
        existing_company = request.user.company

    if request.method == 'POST':
        form = AdvertiseForm(request.POST, request.FILES, existing_company=existing_company)
        if form.is_valid():
            advertiser_request = form.save(commit=False)
            advertiser_request.event = event  

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

# Panel de mis eventos
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

# Formatos de correo (para inscripcion o anulación)
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