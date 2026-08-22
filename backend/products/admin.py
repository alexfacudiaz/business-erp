from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from django.core.exceptions import ValidationError

from .models import Product

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
