from django.db import models
from django.conf import settings


class Category(models.Model):
    """Medicine category."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For emoji or icon class
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Medicine(models.Model):
    """Medicine/Product model."""
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='medicines')
    description = models.TextField()
    
    # Pricing
    mrp = models.DecimalField(max_digits=10, decimal_places=2)  # Maximum Retail Price
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Selling price
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Stock & Distributor
    distributor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'distributor'},
        related_name='medicines'
    )
    stock = models.IntegerField(default=0)
    
    # Product details
    manufacturer = models.CharField(max_length=200)
    composition = models.TextField(blank=True)
    dosage_form = models.CharField(max_length=100, blank=True)  # Tablet, Syrup, etc.
    pack_size = models.CharField(max_length=50, blank=True)  # 10 tablets, 100ml, etc.
    
    # Prescription required
    requires_prescription = models.BooleanField(default=False)
    
    # Image
    image = models.ImageField(upload_to='medicines/', null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.manufacturer}"
    
    @property
    def in_stock(self):
        return self.stock > 0
    
    @property
    def savings(self):
        return self.mrp - self.price
