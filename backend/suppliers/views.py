from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.response import Response

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

    def destroy(self, request, *args, **kwargs):
        supplier = self.get_object()

        supplier.is_active = False
        supplier.save(update_fields=['is_active'])

        return Response(status=status.HTTP_204_NO_CONTENT)