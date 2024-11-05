from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from event.models import Event
from event.forms import EventForm

def companyDashboard(request):
    if request.user.is_company:
        # Eliminar un evento
        if request.method == 'POST' and 'delete_event_id' in request.POST:
            event_id = request.POST.get('delete_event_id')
            event = get_object_or_404(Event, id=event_id, organizer=request.user.company)
            event.delete() 
            messages.success(request, '¡Evento eliminado con éxito!')
            return redirect('companies')

        # Crear evento
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

        # Obtener los eventos organizados por la empresa
        company_events = Event.objects.filter(organizer=request.user.company)

        # Obtener la lista de asistentes por evento
        events_with_attendees = []
        for event in company_events:
            attendees = event.attendees.all()
            events_with_attendees.append({
                'event': event,
                'attendees': attendees
            })

        return render(request, 'companies.html', {
            'form': form,
            'company_events': company_events,
            'events_with_attendees': events_with_attendees,  # Enviar los eventos con asistentes
        })
    
    else:
        messages.error(request, 'Solo las empresas pueden acceder a este panel.')
        return redirect('events')
