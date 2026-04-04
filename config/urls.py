"""
URL configuration for NeuroVaidya project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Auth
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    
    # API endpoints
    path('api/auth/', include('users.urls')),
    path('api/medicines/', include('medicines.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/search/', include('search.urls')),

    
    # Frontend pages (will be served by Django templates)
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('catalog/', TemplateView.as_view(template_name='catalog.html'), name='catalog'),
    path('cart/', TemplateView.as_view(template_name='cart.html'), name='cart'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
