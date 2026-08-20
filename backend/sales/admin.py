from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import Sale, SaleItem
from .services import confirm_sale, cancel_sale

# Register your models here.
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1

    fields = (
        'product',
        'quantity',
        'unit_price',
        'subtotal',
    )

    readonly_fields = (
        'subtotal',
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(
            super().get_readonly_fields(request, obj)
        )

        if obj and obj.status != Sale.Status.DRAFT:
            readonly_fields.extend(
                ('product', 'quantity', 'unit_price')
            )

        return readonly_fields


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'status',
        'reference',
        'created_at',
        'confirmed_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'customer__first_name',
        'customer__last_name',
        'customer__business_name',
        'customer__tax_id',
        'reference',
    )

    ordering = (
        '-created_at',
    )

    readonly_fields = (
        'status',
        'confirmed_at',
        'created_at',
        'updated_at',
    )

    inlines = (
        SaleItemInline,
    )

    actions = (
        'confirm_sales',
        'cancel_sales',
    )

    @admin.action(description='Confirmar ventas seleccionadas')
    def confirm_sales(self, request, queryset):
        sales = queryset.filter(
            status=Sale.Status.DRAFT
        )

        confirmed = 0

        for sale in sales:
            try:
                confirm_sale(sale)
                confirmed += 1
            except ValidationError as error:
                self.message_user(
                    request,
                    f'Venta #{sale.pk}: {error}',
                    level=messages.ERROR,
                )

        if confirmed:
            self.message_user(
                request,
                f'{confirmed} venta(s) confirmada(s) correctamente.',
                level=messages.SUCCESS,
            )

    @admin.action(description='Cancelar ventas seleccionadas')
    def cancel_sales(self, request, queryset):
        sales = queryset.filter(
            status=Sale.Status.CONFIRMED
        )

        cancelled = 0

        for sale in sales:
            try:
                cancel_sale(sale)
                cancelled += 1
            except ValidationError as error:
                self.message_user(
                    request,
                    f'Venta #{sale.pk}: {error}',
                    level=messages.ERROR,
                )

        if cancelled:
            self.message_user(
                request,
                f'{cancelled} venta(s) cancelada(s) correctamente.',
                level=messages.SUCCESS,
            )


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'sale',
        'product',
        'quantity',
        'unit_price',
        'subtotal',
        'created_at',
    )

    list_filter = (
        'sale__status',
    )

    search_fields = (
        'sale__reference',
        'product__name',
        'product__sku',
    )

    readonly_fields = (
        'sale',
        'product',
        'quantity',
        'unit_price',
        'subtotal',
        'created_at',
        'updated_at',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False