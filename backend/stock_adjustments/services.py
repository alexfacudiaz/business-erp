from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from products.models import Product

from .models import StockAdjustment, StockAdjustmentItem


@transaction.atomic
def confirm_stock_adjustment(
    adjustment: StockAdjustment,
    user,
) -> StockAdjustment:

    if adjustment.status != StockAdjustment.Status.DRAFT:
        raise ValidationError(
            'Solo se pueden confirmar ajustes de stock en estado borrador.'
        )

    items = adjustment.items.all() # type: ignore

    if not items.exists():
        raise ValidationError(
            'No se puede confirmar un ajuste de stock sin productos.'
        )

    for item in items:
        product = (
            Product.objects
            .select_for_update()
            .get(pk=item.product_id)
        )

        previous_stock = product.stock

        if item.adjustment_type == StockAdjustmentItem.AdjustmentType.INCREASE:
            new_stock = previous_stock + item.quantity

        else:
            new_stock = previous_stock - item.quantity

            if new_stock < 0:
                raise ValidationError(
                    f'No se puede realizar el ajuste porque el stock de '
                    f'{product} sería negativo.'
                )

        item.previous_stock = previous_stock
        item.new_stock = new_stock

        product.stock = new_stock

        product.save(
            update_fields=[
                'stock',
                'updated_at',
            ]
        )

        item.save(
            update_fields=[
                'previous_stock',
                'new_stock',
                'updated_at',
            ]
        )

    adjustment.status = StockAdjustment.Status.CONFIRMED
    adjustment.confirmed_by = user
    adjustment.confirmed_at = timezone.now()

    adjustment.save(
        update_fields=[
            'status',
            'confirmed_by',
            'confirmed_at',
            'updated_at',
        ]
    )

    return adjustment