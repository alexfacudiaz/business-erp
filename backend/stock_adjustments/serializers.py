from rest_framework import serializers

from .models import StockAdjustment, StockAdjustmentItem


class StockAdjustmentItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockAdjustmentItem
        fields = (
            'id',
            'adjustment',
            'product',
            'adjustment_type',
            'quantity',
            'previous_stock',
            'new_stock',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'previous_stock',
            'new_stock',
            'created_at',
            'updated_at',
        )


class StockAdjustmentSerializer(serializers.ModelSerializer):
    items = StockAdjustmentItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = StockAdjustment
        fields = (
            'id',
            'status',
            'reason',
            'created_by',
            'confirmed_by',
            'confirmed_at',
            'items',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'status',
            'created_by',
            'confirmed_by',
            'confirmed_at',
            'items',
            'created_at',
            'updated_at',
        )