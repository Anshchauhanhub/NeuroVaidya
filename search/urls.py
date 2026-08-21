from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.SearchView.as_view(), name='search'),
    path('ai-chat/', views.AIChatView.as_view(), name='ai_chat'),
    path('external/live/', views.LiveMarketSearchView.as_view(), name='live_market_search'),
    path('external/status/', views.LiveMarketStatusView.as_view(), name='live_market_status'),
    path('nearby/', views.NearbySearchView.as_view(), name='nearby_search'),
]
