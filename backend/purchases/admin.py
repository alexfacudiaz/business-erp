from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import Purchase, PurchaseItem
from .services import confirm_purchase, cancel_purchase

# Register your models here.
class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1

    fields = (
        'product',
        'quantity',
        'unit_cost',
        'subtotal',
    )

    readonly_fields = (
        'subtotal',
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))

        if obj and obj.status != Purchase.Status.DRAFT:
            readonly_fields.extend(
                ('product', 'quantity', 'unit_cost')
            )

        return readonly_fields


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'supplier',
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
        'supplier__first_name',
        'supplier__last_name',
        'supplier__business_name',
        'supplier__tax_id',
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
        PurchaseItemInline,
    )

    actions = (
        'confirm_purchases',
        'cancel_purchases',
    )

    admin.action(description='Confirmar compras seleccionadas')
    def confirm_purchases(self, request, queryset):
        purchases = queryset.filter(
            status=Purchase.Status.DRAFT
        )
        
        confirmed = 0

        for purchase in purchases:
            try:
                confirm_purchase(purchase)
                confirmed += 1
            except ValidationError as error:
                self.message_user(
                    request,
                    f'Compra #{purchase.pk}: {error}',
                    level=messages.ERROR,
                )

        if confirmed:
            self.message_user(
                request,
                f'{confirmed} compra(s) confirmada(s) correctamente.',
                level=messages.SUCCESS,
            )

    @admin.action(description='Cancelar compras seleccionadas')
    def cancel_purchases(self, request, queryset):
        purchases = queryset.filter(
            status=Purchase.Status.CONFIRMED
        )
        
        cancelled = 0

        for purchase in purchases:
            try:
                cancel_purchase(purchase)
                cancelled += 1
            except ValidationError as error:
                self.message_user(
                    request,
                    f'Compra #{purchase.pk}: {error}',
                    level=messages.ERROR,
                )

        if cancelled:
            self.message_user(
                request,
                f'{cancelled} compra(s) cancelada(s) correctamente.',
                level=messages.SUCCESS,
            )


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'purchase',
        'product',
        'quantity',
        'unit_cost',
        'subtotal',
        'created_at',
    )

    list_filter = (
        'purchase__status',
    )

    search_fields = (
        'purchase__reference',
        'product__name',
        'product__sku',
    )

    readonly_fields = (
        'purchase',
        'product',
        'quantity',
        'unit_cost',
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