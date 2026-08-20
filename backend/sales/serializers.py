from rest_framework import serializers

from .models import Sale, SaleItem


class SaleItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = SaleItem
        fields = (
            'id',
            'sale',
            'product',
            'quantity',
            'unit_price',
            'subtotal',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'subtotal',
            'created_at',
            'updated_at',
        )


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Sale
        fields = (
            'id',
            'customer',
            'status',
            'reference',
            'confirmed_at',
            'items',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'status',
            'confirmed_at',
            'items',
            'created_at',
            'updated_at',
        )