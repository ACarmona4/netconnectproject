from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'name', 'last_name', 'documentoIdentidad', 'phone', 'is_company')

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('email', 'name', 'last_name', 'documentoIdentidad', 'phone', 'is_company')
        
User = get_user_model()

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(label="Nombre")
    last_name = forms.CharField(label="Apellido", required=True)
    documentoIdentidad = forms.CharField(label="Documento de Identidad", required=True)
    phone = forms.CharField(label="Teléfono", required=False)

    class Meta:
        model = User
        fields = ["email", "name", "last_name", "documentoIdentidad", "phone", "password1", "password2"]