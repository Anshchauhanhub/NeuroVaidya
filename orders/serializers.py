from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from medicines.serializers import MedicineListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    medicine = MedicineListSerializer(read_only=True)
    medicine_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'medicine', 'medicine_id', 'quantity', 'subtotal']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    coupon_code = serializers.CharField(source='coupon.code', read_only=True, allow_null=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'subtotal', 'discount_amount', 'total_amount', 'coupon_code']


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'medicine_name', 'quantity', 'price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source='patient.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'patient', 'patient_name', 'items',
                  'delivery_address', 'delivery_city', 'delivery_state', 
                  'delivery_pincode', 'delivery_phone',
                  'subtotal', 'discount', 'delivery_charges', 'total_amount',
                  'status', 'status_display', 'payment_status', 'prescription',
                  'created_at']
        read_only_fields = ['order_number', 'patient', 'subtotal', 'total_amount', 'created_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['delivery_address', 'delivery_city', 'delivery_state', 
                  'delivery_pincode', 'delivery_phone', 'prescription']
