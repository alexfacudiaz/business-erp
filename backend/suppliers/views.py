from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from .models import Supplier
from .serializers import SupplierSerializer
from core.permissions import ERPModelPermissions


# Create your views here.
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    filterset_fields = (
        'supplier_type',
        'is_active',
    )

    search_fields = (
        'first_name',
        'last_name',
        'business_name',
        'tax_id',
        'email',
    )

    ordering_fields = (
        'supplier_type',
        'first_name',
        'last_name',
        'business_name',
        'created_at',
    )

    ordering = (
        'supplier_type',
        'last_name',
        'business_name',
    )

    permission_classes = (
        ERPModelPermissions,
    )

    @action(
        detail=True,
        methods=['post'],
    )
    def activate(self, request, pk=None):
        supplier = self.get_object()

        if supplier.is_active:
            raise ValidationError(
                'El proveedor ya está activo.'
            )

        supplier.is_active = True

        supplier.save(
            update_fields=[
                'is_active',
                'updated_at',
            ]
        )

        return Response(
            SupplierSerializer(supplier).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=['post'],
    )
    def deactivate(self, request, pk=None):
        supplier = self.get_object()

        if not supplier.is_active:
            raise ValidationError(
                'El proveedor ya está inactivo.'
            )

        supplier.is_active = False

        supplier.save(
            update_fields=[
                'is_active',
                'updated_at',
            ]
        )

        return Response(
            SupplierSerializer(supplier).data,
            status=status.HTTP_200_OK,
        )