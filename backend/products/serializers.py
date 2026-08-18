from rest_framework import serializers

from .models import Product, StockMovement

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'sku',
            'description',
            'price',
            'cost',
            'stock',
            'min_stock',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'stock',
            'created_at',
            'updated_at',
        )


class StockMovementSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )

    class Meta:
        model = StockMovement
        fields = (
            'id',
            'product',
            'movement_type',
            'quantity',
            'reason',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'created_at',
            'updated_at',
        )

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'La cantidad debe ser mayor que 0.'
            )

        return value