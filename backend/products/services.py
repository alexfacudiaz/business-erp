from decimal import Decimal

from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Product, StockMovement

@transaction.atomic
def create_stock_movement(
    *,
    product: Product,
    movement_type: str,
    quantity: Decimal,
    reason: str = '',
) -> StockMovement:

    if quantity <= 0:
        raise ValidationError(
            {'quantity': 'La cantidad debe ser mayor que 0.'}
        )

    product = (
        Product.objects
        .select_for_update()
        .get(pk=product.pk)
    )
    

    if movement_type == StockMovement.MovementType.IN:
        new_stock = product.stock + quantity

    elif movement_type == StockMovement.MovementType.OUT:
        new_stock = product.stock - quantity

        if new_stock < 0:
            raise ValidationError(
                {'quantity': 'El stock no puede ser negativo.'}
            )

    elif movement_type == StockMovement.MovementType.ADJUSTMENT:
        new_stock = quantity

        if new_stock < 0:
            raise ValidationError(
                {'quantity': 'El stock no puede ser negativo.'}
            )

    else:
        raise ValidationError(
            {'movement_type': 'Tipo de movimiento inválido.'}
        )

    movement = StockMovement.objects.create(
        product=product,
        movement_type=movement_type,
        quantity=quantity,
        reason=reason,
    )

    product.stock = new_stock
    product.save(update_fields=['stock', 'updated_at'])

    return movement