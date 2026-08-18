from django.db import transaction
from django.db.models import F

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, mixins
from rest_framework.exceptions import ValidationError

from .models import Product, StockMovement
from .serializers import ProductSerializer, StockMovementSerializer

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


class StockMovementViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = StockMovement.objects.select_related('product').all()
    serializer_class = StockMovementSerializer

    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )

    filterset_fields = (
        'product',
        'movement_type',
    )

    ordering_fields = (
        'created_at',
        'quantity',
        'movement_type',
    )

    ordering = (
        '-created_at',
    )

    def perform_create(self, serializer):
        with transaction.atomic():
            movement = serializer.save()
            self._update_stock(movement)

    def _update_stock(self, movement):
        product = (
            Product.objects
            .select_for_update()
            .get(pk=movement.product_id)
        )

        if movement.movement_type == StockMovement.MovementType.IN:
            product.stock += movement.quantity

        elif movement.movement_type == StockMovement.MovementType.OUT:
            new_stock = product.stock - movement.quantity

            if new_stock < 0:
                raise ValidationError(
                    'No hay stock suficiente para realizar el egreso.'
                )

            product.stock = new_stock

        elif movement.movement_type == StockMovement.MovementType.ADJUSTMENT:
            product.stock = movement.quantity

        product.save(update_fields=['stock', 'updated_at'])