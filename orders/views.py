from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderCreateSerializer
from medicines.models import Medicine
from django.contrib.auth import get_user_model

User = get_user_model()


class CartView(APIView):
    """Get or manage user's cart."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartCountView(APIView):
    """Get cart item count for header badge."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            count = sum(item.quantity for item in cart.items.all())
        else:
            count = 0
        return Response({'count': count})


class AddToCartView(APIView):
    """Add item to cart."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        medicine_id = request.data.get('medicine_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            medicine = Medicine.objects.get(id=medicine_id, is_active=True)
        except Medicine.DoesNotExist:
            return Response({'error': 'Medicine not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if medicine.stock < quantity:
            return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            medicine=medicine,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return Response(CartSerializer(cart).data)


class AddExternalToCartView(APIView):
    """Add external scraped item to cart by creating a Medicine entry on the fly."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        name = request.data.get('name')
        price = request.data.get('price')
        mrp = request.data.get('mrp')
        source_site = request.data.get('source_site', 'External Platform')
        image_url = request.data.get('image_url', '')
        quantity = int(request.data.get('quantity', 1))
        
        if not name or price is None:
            return Response({'error': 'Name and price required'}, status=status.HTTP_400_BAD_REQUEST)
            
        distributor = User.objects.filter(role__in=['distributor', 'admin']).first()
        if not distributor:
            distributor = User.objects.first()
            
        try:
            price_val = float(str(price).replace('₹', '').replace(',', '').strip() or 0)
        except ValueError:
            price_val = 0
            
        try:
            mrp_val = float(str(mrp).replace('₹', '').replace(',', '').strip() or price_val)
        except ValueError:
            mrp_val = price_val

        medicine, created = Medicine.objects.get_or_create(
            name=name,
            manufacturer=source_site,
            defaults={
                'price': price_val,
                'mrp': mrp_val,
                'distributor': distributor,
                'description': image_url,
                'stock': 999,
                'is_active': True,
            }
        )

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            medicine=medicine,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return Response(CartSerializer(cart).data)


class UpdateCartItemView(APIView):
    """Update cart item quantity."""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, item_id):
        quantity = int(request.data.get('quantity', 1))
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if quantity <= 0:
            cart_item.delete()
        else:
            if cart_item.medicine.stock < quantity:
                return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = quantity
            cart_item.save()
        
        cart = Cart.objects.get(user=request.user)
        return Response(CartSerializer(cart).data)
    
    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass
        
        cart = Cart.objects.get(user=request.user)
        return Response(CartSerializer(cart).data)


from django.utils import timezone
from .models import Cart, CartItem, Order, OrderItem, Coupon

class ApplyCouponView(APIView):
    """Apply coupon to cart."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Coupon code required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            now = timezone.now()
            if coupon.valid_from and coupon.valid_from > now:
                return Response({'error': 'Coupon not yet valid'}, status=status.HTTP_400_BAD_REQUEST)
            if coupon.valid_to and coupon.valid_to < now:
                return Response({'error': 'Coupon expired'}, status=status.HTTP_400_BAD_REQUEST)
                
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart.coupon = coupon
            cart.save()
            return Response({'message': 'Coupon applied', 'discount': coupon.discount_percent})
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid coupon code'}, status=status.HTTP_400_BAD_REQUEST)

class RemoveCouponView(APIView):
    """Remove coupon from cart."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.coupon = None
        cart.save()
        return Response({'message': 'Coupon removed'})


class CheckoutView(APIView):
    """Create order from cart."""
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Calculate totals
        raw_subtotal = sum(item.subtotal for item in cart.items.all())
        discount = 0
        if cart.coupon and cart.coupon.is_active:
            discount = (raw_subtotal * cart.coupon.discount_percent) / 100
            
        subtotal_after_discount = raw_subtotal - discount
        delivery_charges = 0 if subtotal_after_discount >= 500 else 50
        total = subtotal_after_discount + delivery_charges
        
        # Create order
        order = Order.objects.create(
            patient=request.user,
            subtotal=raw_subtotal,
            discount=discount,
            delivery_charges=delivery_charges,
            total_amount=total,
            **serializer.validated_data
        )
        
        # Create order items and reduce stock
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                medicine=cart_item.medicine,
                medicine_name=cart_item.medicine.name,
                quantity=cart_item.quantity,
                price=cart_item.medicine.price
            )
            # Reduce stock
            cart_item.medicine.stock -= cart_item.quantity
            cart_item.medicine.save()
        
        # Clear cart
        cart.items.all().delete()
        cart.coupon = None
        cart.save()
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    """List user's orders."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(patient=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    """Get order details."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(patient=self.request.user)
