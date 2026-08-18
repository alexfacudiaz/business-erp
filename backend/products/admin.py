from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from django.core.exceptions import ValidationError

from .models import Product, StockMovement
from .services import create_stock_movement

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'sku',
        'price',
        'cost',
        'stock',
        'min_stock',
        'is_active',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'name',
        'sku',
    )

    ordering = (
        'name',
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'movement_type',
        'quantity',
        'reason',
        'created_at',
    )

    list_filter = (
        'movement_type',
        'created_at',
    )

    search_fields = (
        'product__name',
        'product__sku',
        'reason',
    )

    ordering = (
        '-created_at',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    def save_model(self, request: HttpRequest, obj: Any, form: Any, change: Any) -> None:
        if change:
            raise ValidationError(
                'Los movimientos de stock no pueden modificarse.'
            )

        movement = create_stock_movement(
            product=obj.product,
            movement_type=obj.movement_type,
            quantity=obj.quantity,
            reason=obj.reason
        )

        obj.pk = movement.pk

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = ...) -> bool:
        return False