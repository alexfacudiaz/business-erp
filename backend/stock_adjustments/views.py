from django.core.exceptions import ValidationError as DjangoValidationError

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import StockAdjustment, StockAdjustmentItem
from .serializers import StockAdjustmentSerializer, StockAdjustmentItemSerializer
from .services import confirm_stock_adjustment
from core.permissions import ERPModelPermissions


# Create your views here.
class StockAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = StockAdjustment.objects.prefetch_related(
        'items'
    ).select_related(
        'created_by',
        'confirmed_by',
    ).all()

    serializer_class = StockAdjustmentSerializer

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    filterset_fields = (
        'status',
        'created_by',
        'confirmed_by',
    )

    search_fields = (
        'reason',
    )

    ordering_fields = (
        'created_at',
        'updated_at',
        'status',
        'confirmed_at',
    )

    ordering = (
        '-created_at',
    )

    permission_classes = (
        ERPModelPermissions,
    )

    @action(
        detail=True,
        methods=['post'],
    )
    def confirm(self, request, pk=None):
        adjustment = self.get_object()

        try:
            confirm_stock_adjustment(
                adjustment,
                request.user,
            )
        except DjangoValidationError as error:
            return Response(
                {'detail': error.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            StockAdjustmentSerializer(adjustment).data,
            status=status.HTTP_200_OK,
        )

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        adjustment = self.get_object()

        if adjustment.status != StockAdjustment.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden modificar ajustes de stock en estado DRAFT.'
            )

        serializer.save()

    def perform_destroy(self, instance):
        if instance.status != StockAdjustment.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden eliminar ajustes de stock en estado DRAFT.'
            )

        instance.delete()


class StockAdjustmentItemViewSet(viewsets.ModelViewSet):
    queryset = StockAdjustmentItem.objects.select_related(
        'adjustment',
        'product',
    ).all()

    serializer_class = StockAdjustmentItemSerializer

    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )

    filterset_fields = (
        'adjustment',
        'product',
        'adjustment_type',
    )

    ordering_fields = (
        'created_at',
        'quantity',
        'previous_stock',
        'new_stock',
    )

    ordering = (
        '-created_at',
    )

    permission_classes = (
        ERPModelPermissions,
    )

    def perform_create(self, serializer):
        adjustment = serializer.validated_data['adjustment']

        if adjustment.status != StockAdjustment.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden agregar items a ajustes de stock '
                'en estado DRAFT.'
            )

        serializer.save()

    def perform_update(self, serializer):
        adjustment = serializer.instance.adjustment

        if adjustment.status != StockAdjustment.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden modificar items de ajustes de stock '
                'en estado DRAFT.'
            )

        serializer.save()

    def perform_destroy(self, instance):
        if instance.adjustment.status != StockAdjustment.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden eliminar items de ajustes de stock '
                'en estado DRAFT.'
            )

        instance.delete()