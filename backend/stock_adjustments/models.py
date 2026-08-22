from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from core.models import TimeStampedModel
from products.models import Product


User = get_user_model()


# Create your models here.
class StockAdjustment(TimeStampedModel):

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Borrador'
        CONFIRMED = 'CONFIRMED', 'Confirmado'

    status = models.CharField(
        max_length=9,
        choices=Status.choices,
        default=Status.DRAFT
    )

    reason = models.TextField(
        blank=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_stock_adjustments',
    )

    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='confirmed_stock_adjustments',
        null=True,
        blank=True
    )

    confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'Ajuste #{self.pk}'


class StockAdjustmentItem(TimeStampedModel):

    class AdjustmentType(models.TextChoices):
        INCREASE = 'INCREASE', 'Aumento'
        DECREASE = 'DECREASE', 'Disminución'

    adjustment = models.ForeignKey(
        StockAdjustment,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='stock_adjustment_items'
    )

    adjustment_type = models.CharField(
        max_length=8,
        choices=AdjustmentType.choices
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3
    )

    previous_stock = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True
    )

    new_stock = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('adjustment', 'product'),
                name='unique_product_per_adjustment',
            ),
        ]

    def clean(self) -> None:
        super().clean()

        if self.quantity is not None and self.quantity <= 0:
            raise ValidationError(
                {'quantity': 'La cantidad debe ser mayor que 0.'}
            )

        if self.previous_stock is not None and self.previous_stock < 0:
            raise ValidationError(
                {'previous_stock': 'El stock anterior no puede ser negativo.'}
            )

        if self.new_stock is not None and self.new_stock < 0:
            raise ValidationError(
                {'new_stock': 'El stock resultante no puede ser negativo.'}
            )

    def __str__(self) -> str:
        return f'{self.product} - {self.quantity}'