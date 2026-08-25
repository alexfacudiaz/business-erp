from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.response import Response

from .models import Customer
from .serializers import CustomerSerializer
from core.permissions import ERPModelPermissions

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )

    filterset_fields = (
        'customer_type',
        'is_active'
    )

    search_fields = (
        'first_name',
        'last_name',
        'business_name',
        'tax_id',
        'email',
    )

    ordering_fields = (
        'customer_type',
        'first_name',
        'last_name',
        'business_name',
        'created_at',
    )

    ordering = (
        'customer_type',
        'last_name',
        'business_name',
    )

    permission_classes = (
        ERPModelPermissions,
    )

    def destroy(self, request, *args, **kwargs):
        customer = self.get_object()

        customer.is_active = False
        customer.save(update_fields=['is_active'])

        return Response(status=status.HTTP_204_NO_CONTENT)