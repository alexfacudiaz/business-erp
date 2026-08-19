from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from products.models import Product
from .models import Purchase

@transaction.atomic
def confirm_purchase(purchase: Purchase) -> Purchase:
    if purchase.status != Purchase.Status.DRAFT:
        raise ValidationError(
            'Solo se pueden confirmar compras en estado borrador.'
        )

    items = purchase.items.all() # type: ignore

    if not items.exists():
        raise ValidationError(
            'No se puede confirmar una compra sin productos.'
        )

    for item in items:
        product = (
            Product.objects
            .select_for_update()
            .get(pk=item.product_id)
        )

        product.stock += item.quantity

        product.save(
            update_fields=[
                'stock',
                'updated_at',
            ]
        )

    purchase.status = Purchase.Status.CONFIRMED
    purchase.confirmed_at = timezone.now()

    purchase.save(
        update_fields=[
            'status',
            'confirmed_at',
            'updated_at',
        ]
    )

    return purchase


@transaction.atomic
def cancel_purchase(purchase: Purchase) -> Purchase:
    if purchase.status != Purchase.Status.CONFIRMED:
        raise ValidationError(
            'Solo se pueden cancelar compras confirmadas.'
        )

    items = purchase.items.all() # type: ignore

    for item in items:
        product = (
            Product.objects
            .select_for_update()
            .get(pk=item.product_id)
        )

        new_stock = product.stock - item.quantity

        if new_stock < 0:
            raise ValidationError(
                f'No se puede cancelar la compra porque el stock de '
                f'{product} sería negativo.'
            )

        product.stock = new_stock

        product.save(
            update_fields=[
                'stock',
                'updated_at',
            ]
        )

    purchase.status = Purchase.Status.CANCELLED

    purchase.save(
        update_fields=[
            'status',
            'updated_at',
        ]
    )

    return purchase