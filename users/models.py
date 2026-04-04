from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model for NeuroVaidya platform."""
    
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('pharmacist', 'Pharmacist'),
        ('admin', 'Admin'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    
    # Profile Picture
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Business-specific fields (for pharmacists/admins)
    company_name = models.CharField(max_length=200, blank=True)
    gst_number = models.CharField(max_length=20, blank=True)
    drug_license = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    
    # Online Status (for consultations)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_patient(self):
        return self.role == 'patient'
    
    @property
    def is_pharmacist(self):
        return self.role == 'pharmacist'
    
    
    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser
