from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'picture']
        
        labels = {
            'name': 'Nombre del evento',
            'description': 'Descripción',
            'date': 'Fecha',
            'time': 'Hora',
            'location': 'Ubicación',
            'picture': 'Imagen del evento',
        }
        
        help_texts = {
            'name': 'Escribe el nombre del evento.',
            'description': 'Añade una breve descripción del evento.',
            'date': 'Selecciona la fecha en que se realizará el evento.',
            'time': 'Selecciona la hora del evento.',
            'location': 'Indica el lugar donde se realizará el evento.',
            'picture': 'Sube una imagen representativa del evento.',
        }
        
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }