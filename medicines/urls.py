from django.urls import path
from . import views

app_name = 'medicines'

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('', views.MedicineListView.as_view(), name='medicine-list'),
    path('<int:pk>/', views.MedicineDetailView.as_view(), name='medicine-detail'),
]
