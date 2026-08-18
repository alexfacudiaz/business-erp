from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import TimeStampedModel

# Create your models here.
class Product(TimeStampedModel):

    name = models.CharField(
        max_length=200
    )

    sku = models.CharField(
        max_length=50,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0')
    )

    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0')
    )

    stock = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0')
    )

    min_stock = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0')
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self) -> str:
        return f'{self.name} ({self.sku})'


class StockMovement(TimeStampedModel):

    class MovementType(models.TextChoices):
        IN = 'IN', 'Ingreso'
        OUT = 'OUT', 'Egreso'
        ADJUSTMENT = 'ADJUSTMENT', 'Ajuste'

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='stock_movements'
    )

    movement_type = models.CharField(
        max_length=10,
        choices=MovementType.choices
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3
    )

    reason = models.CharField(
        max_length=255,
        blank=True
    )

    def clean(self) -> None:
        super().clean()

        if self.quantity <= 0:
            raise ValidationError(
                {'quantity': 'La cantidad debe ser mayor que 0.'}
            )

    def __str__(self) -> str:
        return (
            f'{self.product} - '
            f'{self.get_movement_type_display()} - ' # type: ignore
            f'{self.quantity}'
        )