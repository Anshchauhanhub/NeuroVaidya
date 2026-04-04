from rest_framework import serializers
from .models import Category, Medicine
from users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    medicine_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'medicine_count']
    
    def get_medicine_count(self, obj):
        return obj.medicines.filter(is_active=True).count()


class MedicineListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Medicine
        fields = ['id', 'name', 'generic_name', 'category', 'category_name',
                  'price', 'mrp', 'discount_percent', 'stock', 'in_stock',
                  'manufacturer', 'image', 'requires_prescription', 'savings']


class MedicineDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Medicine
        fields = ['id', 'name', 'generic_name', 'category', 'description',
                  'price', 'mrp', 'discount_percent', 'stock', 'in_stock',
                  'manufacturer', 'composition', 'dosage_form', 'pack_size',
                  'image', 'requires_prescription', 'savings',
                  'created_at']


class MedicineCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ['name', 'generic_name', 'category', 'description',
                  'price', 'mrp', 'discount_percent', 'stock',
                  'manufacturer', 'composition', 'dosage_form', 'pack_size',
                  'image', 'requires_prescription']
