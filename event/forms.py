from django import forms
from .models import Event
from company.models import Company

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'picture', 'participants']  
        
        labels = {
            'name': 'Nombre del evento',
            'description': 'Descripción',
            'date': 'Fecha',
            'time': 'Hora',
            'location': 'Ubicación',
            'picture': 'Imagen del evento',
            'participants': 'Empresas participantes' 
        }
        
        help_texts = {
            'name': 'Escribe el nombre del evento.',
            'description': 'Añade una breve descripción del evento.',
            'date': 'Selecciona la fecha en que se realizará el evento.',
            'time': 'Selecciona la hora del evento.',
            'location': 'Indica el lugar donde se realizará el evento.',
            'picture': 'Sube una imagen representativa del evento.',
            'participants': 'Selecciona las empresas que participarán en este evento.' 
        }
        
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'participants': forms.CheckboxSelectMultiple()  
        }

    participants = forms.ModelMultipleChoiceField(
        queryset=Company.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Empresas participantes",  
        help_text="Selecciona las empresas que participarán en este evento."  
    )