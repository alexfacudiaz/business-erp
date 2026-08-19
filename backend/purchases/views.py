from django.core.exceptions import ValidationError as DjangoValidationError

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Purchase, PurchaseItem
from .serializers import PurchaseSerializer, PurchaseItemSerializer
from .services import confirm_purchase, cancel_purchase

# Create your views here.
class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.prefetch_related(
        'items'
    ).select_related(
        'supplier'
    ).all()

    serializer_class = PurchaseSerializer

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    filterset_fields = (
        'reference',
        'supplier__first_name',
        'supplier__last_name',
        'supplier__business_name',
        'supplier__tax_id',
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

    @action(
        detail=True,
        methods=['post'],
    )
    def confirm(self, request, pk=None):
        purchase = self.get_object()

        try:
            confirm_purchase(purchase)
        except DjangoValidationError as error:
            return Response(
                {'detail': error.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            PurchaseSerializer(purchase).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=['post'],
    )
    def cancel(self, request, pk=None):
        purchase = self.get_object()

        try:
            cancel_purchase(purchase)
        except DjangoValidationError as error:
            return Response(
                {'detail': error.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            PurchaseSerializer(purchase).data,
            status=status.HTTP_200_OK,
        )

    def perform_update(self, serializer):
        purchase = self.get_object()

        if purchase.status != Purchase.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden modificar compras en estado DRAFT.'
            )

        serializer.save()

    def perform_destroy(self, instance):
        if instance.status != Purchase.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden eliminar compras en estado DRAFT.'
            )

        instance.delete()


class PurchaseItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseItem.objects.select_related(
        'purchase',
        'product',
    ).all()

    serializer_class = PurchaseItemSerializer

    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )

    filterset_fields = (
        'purchase',
        'product',
    )

    ordering_fields = (
        'created_at',
        'quantity',
        'unit_cost',
    )

    ordering = (
        '-created_at',
    )

    def perform_create(self, serializer):
        purchase = serializer.validated_data['purchase']

        if purchase.status != Purchase.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden agregar items a compras en estado DRAFT.'
            )

        serializer.save()

    def perform_update(self, serializer):
        purchase = serializer.instance.purchase

        if purchase.status != Purchase.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden modificar items de compras en estado DRAFT.'
            )

        serializer.save()

    def perform_destroy(self, instance):
        if instance.purchase.status != Purchase.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden eliminar items de compras en estado DRAFT.'
            )

        instance.delete()