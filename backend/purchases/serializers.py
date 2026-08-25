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

    def validate(self, attrs):
        quantity = attrs.get('quantity')
        unit_cost = attrs.get('unit_cost')

        if quantity is not None and quantity <= 0:
            raise serializers.ValidationError({
                'quantity': 'La cantidad debe ser mayor que 0.'
            })

        if unit_cost is not None and unit_cost < 0:
            raise serializers.ValidationError({
                'unit_cost': 'El costo unitario no puede ser negativo.'
            })

        return attrs


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