from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm  
from event.models import Event 

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
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_company = False  
            user.save()
            login(request, user)  

            if next_event_id:
                event = Event.objects.filter(id=next_event_id).first()
                if event:
                    event.attendees.add(user)  

            return redirect('event_detail', event_id=next_event_id if next_event_id else 'home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})