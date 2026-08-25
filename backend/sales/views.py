from django.core.exceptions import ValidationError as DjangoValidationError

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Sale, SaleItem
from .serializers import SaleSerializer, SaleItemSerializer
from .services import confirm_sale, cancel_sale
from core.permissions import ERPModelPermissions

# Create your views here.
class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.prefetch_related(
        'items'
    ).select_related(
        'customer'
    ).all()

    serializer_class = SaleSerializer

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    filterset_fields = (
        'reference',
        'customer__first_name',
        'customer__last_name',
        'customer__business_name',
        'customer__tax_id',
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
        sale = self.get_object()

        try:
            confirm_sale(sale)
        except DjangoValidationError as error:
            return Response(
                {'detail': error.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            SaleSerializer(sale).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=['post'],
    )
    def cancel(self, request, pk=None):
        sale = self.get_object()

        try:
            cancel_sale(sale)
        except DjangoValidationError as error:
            return Response(
                {'detail': error.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            SaleSerializer(sale).data,
            status=status.HTTP_200_OK,
        )

    def perform_update(self, serializer):
        sale = self.get_object()

        if sale.status != Sale.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden modificar ventas en estado DRAFT.'
            )

        serializer.save()

    def perform_destroy(self, instance):
        if instance.status != Sale.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden eliminar ventas en estado DRAFT.'
            )

        instance.delete()


class SaleItemViewSet(viewsets.ModelViewSet):
    queryset = SaleItem.objects.select_related(
        'sale',
        'product',
    ).all()

    serializer_class = SaleItemSerializer

    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )

    filterset_fields = (
        'sale',
        'product',
    )

    ordering_fields = (
        'created_at',
        'quantity',
        'unit_price',
    )

    ordering = (
        '-created_at',
    )

    permission_classes = (
        ERPModelPermissions,
    )

    def perform_create(self, serializer):
        sale = serializer.validated_data['sale']

        if sale.status != Sale.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden agregar items a ventas en estado DRAFT.'
            )

        serializer.save()

    def perform_update(self, serializer):
        sale = serializer.instance.sale

        if sale.status != Sale.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden modificar items de ventas en estado DRAFT.'
            )

        serializer.save()

    def perform_destroy(self, instance):
        if instance.sale.status != Sale.Status.DRAFT:
            raise ValidationError(
                'Solo se pueden eliminar items de ventas en estado DRAFT.'
            )

        instance.delete()