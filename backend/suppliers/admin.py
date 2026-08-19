from django.contrib import admin

from .models import Supplier

# Register your models here.
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        'display_name',
        'supplier_type',
        'tax_id',
        'email',
        'is_active',
    )

    list_filter = (
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

    ordering = (
        'supplier_type',
        'last_name',
        'business_name',
    )

    @admin.display(description='Name')
    def display_name(self, obj):
        return str(obj)