from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['email', 'name', 'last_name', 'is_company']
    list_filter = ['is_company', 'is_staff', 'is_superuser']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('name', 'last_name', 'phone')}),
        ('Permisos', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
        ('Company', {'fields': ('is_company', 'logo')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'last_name', 'phone', 'password1', 'password2', 'is_company', 'logo', 'is_staff', 'is_superuser'),
        }),
    )

    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)