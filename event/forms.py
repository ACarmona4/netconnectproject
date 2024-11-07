from django import forms
from .models import Event
from company.models import Company
from .models import AdvertiserRequest

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

class AdvertiseForm(forms.ModelForm):
    class Meta:
        model = AdvertiserRequest
        fields = ['company_name', 'contact_name', 'contact_email', 'logo', 'description', 'message']
        labels = {
            'company_name': 'Nombre de la Empresa',
            'contact_name': 'Nombre de Contacto',
            'contact_email': 'Correo Electrónico de Contacto',
            'logo': 'Logo de la Empresa',
            'description': 'Descripción de la Empresa',
            'message': 'Mensaje de Solicitud'
        }

    def __init__(self, *args, **kwargs):
        # Recibe una empresa existente, si está en los argumentos
        existing_company = kwargs.pop('existing_company', None)
        super().__init__(*args, **kwargs)

        if existing_company:
            # Si la empresa ya existe, oculta todos los campos excepto el mensaje
            for field in ['company_name', 'contact_name', 'contact_email', 'logo', 'description']:
                if field in self.fields:
                    self.fields[field].widget = forms.HiddenInput()
                    self.fields[field].required = False

            # Inicializa los campos con los datos de la empresa existente
            self.fields['company_name'].initial = existing_company.name
            self.fields['contact_name'].initial = existing_company.personInCharge
            self.fields['contact_email'].initial = existing_company.email
            self.fields['logo'].initial = existing_company.logo
            self.fields['description'].initial = existing_company.description