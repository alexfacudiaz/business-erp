from rest_framework import serializers

from .models import Purchase, PurchaseItem


class PurchaseItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseItem
        fields = (
            'id',
            'product',
            'purchase',
            'quantity',
            'unit_cost',
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


class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Purchase
        fields = (
            'id',
            'supplier',
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