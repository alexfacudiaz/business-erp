from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from products.models import Product
from .models import Sale

@transaction.atomic
def confirm_sale(sale: Sale) -> Sale:
    if sale.status != Sale.Status.DRAFT:
        raise ValidationError(
            'Solo se pueden confirmar ventas en estado borrador.'
        )

    items = sale.items.all()  # type: ignore

    if not items.exists():
        raise ValidationError(
            'No se puede confirmar una venta sin productos.'
        )

    for item in items:
        product = (
            Product.objects
            .select_for_update()
            .get(pk=item.product_id)
        )

        new_stock = product.stock - item.quantity

        if new_stock < 0:
            raise ValidationError(
                f'No hay stock suficiente para el producto {product}.'
            )

        product.stock = new_stock

        product.save(
            update_fields=[
                'stock',
                'updated_at',
            ]
        )

    sale.status = Sale.Status.CONFIRMED
    sale.confirmed_at = timezone.now()

    sale.save(
        update_fields=[
            'status',
            'confirmed_at',
            'updated_at',
        ]
    )

    return sale


@transaction.atomic
def cancel_sale(sale: Sale) -> Sale:
    if sale.status != Sale.Status.CONFIRMED:
        raise ValidationError(
            'Solo se pueden cancelar ventas confirmadas.'
        )

    items = sale.items.all()  # type: ignore

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

    sale.status = Sale.Status.CANCELLED

    sale.save(
        update_fields=[
            'status',
            'updated_at',
        ]
    )

    return sale