from django.db import transaction
from django.db.models import F

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, mixins
from rest_framework.exceptions import ValidationError

from .models import Product
from .serializers import ProductSerializer

# Create your views here.
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    filterset_fields = (
        'name',
        'sku',
        'description',
    )

    ordering_fields = (
        'name',
        'sku',
        'price',
        'cost',
        'stock',
        'min_stock',
        'created_at',
    )

    ordering = (
        'name',
    )
