from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Cart
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/count/', views.CartCountView.as_view(), name='cart-count'),
    path('cart/add/', views.AddToCartView.as_view(), name='cart-add'),
    path('cart/add_external/', views.AddExternalToCartView.as_view(), name='cart-add-external'),
    path('cart/item/<int:item_id>/', views.UpdateCartItemView.as_view(), name='cart-item'),
    
    # Checkout & Orders
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('apply-coupon/', views.ApplyCouponView.as_view(), name='apply_coupon'),
    path('remove-coupon/', views.RemoveCouponView.as_view(), name='remove_coupon'),
    path('', views.OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
]
