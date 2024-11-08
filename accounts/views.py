from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm  
from event.models import Event 
from django.urls import reverse
from io import BytesIO
import qrcode
from django.core.files.base import ContentFile
from event.models import Attendance

# Create your views here.

def loginView(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Credenciales inválidas para usuarios.')
    
    return render(request, 'login.html')

def logoutView(request):
    logout(request)
    return redirect('home')


def register(request):
    next_event_id = request.GET.get('next_event')  
    event = None
    if next_event_id:
        event = Event.objects.filter(id=next_event_id).first()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_company = False  
            user.save()
            login(request, user)  

            if event:
                event.attendees.add(user)
                attendance = Attendance.objects.create(user=user, event=event)

                qr_url = request.build_absolute_uri(reverse('verify_qr_code', args=[user.id, event.id]))
                qr = qrcode.make(qr_url)
                qr_io = BytesIO()
                qr.save(qr_io, 'PNG')

                attendance.qr_code.save(f"qr_{user.id}_{event.id}.png", ContentFile(qr_io.getvalue()))

            return redirect('my_events')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form, 'event': event})