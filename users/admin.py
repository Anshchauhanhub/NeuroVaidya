from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_verified', 'is_active')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone', 'company_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('NeuroVaidya Info', {
            'fields': ('role', 'phone', 'address', 'city', 'state', 'pincode')
        }),
        ('Business Info', {
            'fields': ('company_name', 'gst_number', 'drug_license', 'is_verified'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('NeuroVaidya Info', {
            'fields': ('role', 'phone', 'email')
        }),
    )
