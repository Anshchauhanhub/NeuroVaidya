from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Medicine
from .serializers import (
    CategorySerializer, 
    MedicineListSerializer, 
    MedicineDetailSerializer,
    MedicineCreateSerializer
)


class CategoryListView(generics.ListAPIView):
    """List all medicine categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class MedicineListView(generics.ListAPIView):
    """List all medicines with search and filtering."""
    queryset = Medicine.objects.filter(is_active=True).select_related('category')
    serializer_class = MedicineListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'generic_name', 'manufacturer', 'category__name']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by prescription requirement
        prescription = self.request.query_params.get('prescription')
        if prescription == 'true':
            queryset = queryset.filter(requires_prescription=True)
        elif prescription == 'false':
            queryset = queryset.filter(requires_prescription=False)
        
        # Filter by stock availability
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(stock__gt=0)
        
        return queryset


class MedicineDetailView(generics.RetrieveAPIView):
    """Get medicine detail."""
    queryset = Medicine.objects.filter(is_active=True)
    serializer_class = MedicineDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
