from rest_framework import serializers

from .models import Product

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

