from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import StockAdjustment, StockAdjustmentItem
from .services import confirm_stock_adjustment


# Register your models here.
class StockAdjustmentItemInline(admin.TabularInline):
    model = StockAdjustmentItem
    extra = 1

    fields = (
        'product',
        'adjustment_type',
        'quantity',
        'previous_stock',
        'new_stock',
    )

    readonly_fields = (
        'previous_stock',
        'new_stock',
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(
            super().get_readonly_fields(request, obj)
        )

        if obj and obj.status != StockAdjustment.Status.DRAFT:
            readonly_fields.extend(
                (
                    'product',
                    'adjustment_type',
                    'quantity',
                )
            )

        return readonly_fields


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'status',
        'reason',
        'created_by',
        'confirmed_by',
        'confirmed_at',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'reason',
        'created_by__username',
        'confirmed_by__username',
    )

    readonly_fields = (
        'status',
        'created_by',
        'confirmed_by',
        'confirmed_at',
        'created_at',
        'updated_at',
    )

    inlines = (
        StockAdjustmentItemInline,
    )

    actions = (
    'confirm_adjustments',
    )

    @admin.action(description='Confirmar ajustes seleccionados')
    def confirm_adjustments(self, request, queryset):

        adjustments = queryset.filter(
            status=StockAdjustment.Status.DRAFT
        )

        confirmed = 0

        for adjustment in adjustments:
            try:
                confirm_stock_adjustment(
                    adjustment,
                    request.user,
                )
                confirmed += 1

            except ValidationError as error:
                self.message_user(
                    request,
                    f'Ajuste #{adjustment.pk}: {error}',
                    level=messages.ERROR,
                )

        if confirmed:
            self.message_user(
                request,
                f'{confirmed} ajuste(s) confirmado(s) correctamente.',
                level=messages.SUCCESS,
            )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user

        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.status != StockAdjustment.Status.DRAFT:
            return False

        return super().has_change_permission(request, obj)


    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.status != StockAdjustment.Status.DRAFT:
            return False

        return super().has_delete_permission(request, obj)


@admin.register(StockAdjustmentItem)
class StockAdjustmentItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'adjustment',
        'product',
        'adjustment_type',
        'quantity',
        'previous_stock',
        'new_stock',
        'created_at',
    )

    list_filter = (
        'adjustment__status',
        'adjustment_type',
    )

    search_fields = (
        'adjustment__reason',
        'product__name',
        'product__sku',
    )

    readonly_fields = (
        'adjustment',
        'product',
        'adjustment_type',
        'quantity',
        'previous_stock',
        'new_stock',
        'created_at',
        'updated_at',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False