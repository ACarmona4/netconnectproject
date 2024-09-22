from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

#Register your models here.
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'last_name', 'phone', 'is_company', 'logo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_company', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    list_display = ('email', 'name', 'last_name', 'is_company', 'is_staff')
    search_fields = ('email', 'name', 'last_name')
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)