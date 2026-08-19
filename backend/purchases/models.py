from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError

from core.models import TimeStampedModel
from products.models import Product
from suppliers.models import Supplier

# Create your models here.
class Purchase(TimeStampedModel):

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Borrador'
        CONFIRMED = 'CONFIRMED', 'Confirmada'
        CANCELLED = 'CANCELLED', 'Cancelada'

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchases'
    )

    status = models.CharField(
        max_length=9,
        choices=Status.choices,
        default=Status.DRAFT
    )

    reference = models.CharField(
        max_length=100,
        blank=True
    )

    confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'Compra #{self.pk} - {self.supplier}'


class PurchaseItem(TimeStampedModel):

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='purchase_items'
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3
    )

    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('purchase', 'product'),
                name='unique_product_per_purchase'
            ),
        ]

    def clean(self) -> None:
        super().clean()

        if self.quantity <= 0:
            raise ValidationError(
                {'quantity': 'La cantidad debe ser mayor que 0.'}
            )
        
        if self.unit_cost < 0:
            raise ValidationError(
                {'unit_cost': 'El costo unitario no puede ser negativo.'}
            )

        if self.purchase_id and self.purchase.status != Purchase.Status.DRAFT: # type: ignore
            raise ValidationError(
                'No se pueden modificar los items de una compra '
                'que no está en estado borrador.'
            )

    @property
    def subtotal(self) -> Decimal:
        if self.quantity is None or self.unit_cost is None:
            return Decimal('0')
        return self.quantity * self.unit_cost

    def __str__(self) -> str:
        return f'{self.product} - {self.quantity}'