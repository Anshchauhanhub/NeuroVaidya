from django.contrib import admin
from .models import Category, Medicine


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'mrp', 'stock', 'is_active')
    list_filter = ('category', 'requires_prescription', 'is_active')
    search_fields = ('name', 'generic_name', 'manufacturer')
    list_editable = ('stock', 'is_active')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'generic_name', 'category', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('mrp', 'price', 'discount_percent')
        }),
        ('Stock Info', {
            'fields': ('stock',)
        }),
        ('Product Details', {
            'fields': ('manufacturer', 'composition', 'dosage_form', 'pack_size')
        }),
        ('Settings', {
            'fields': ('requires_prescription', 'is_active')
        }),
    )
