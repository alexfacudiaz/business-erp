from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError

from core.models import TimeStampedModel
from customers.models import Customer
from products.models import Product

# Create your models here.
class Sale(TimeStampedModel):

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Borrador'
        CONFIRMED = 'CONFIRMED', 'Confirmada'
        CANCELLED = 'CANCELLED', 'Cancelada'

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='sales'
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
        return f'Venta #{self.pk} - {self.customer}'


class SaleItem(TimeStampedModel):

    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='sale_items'
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('sale', 'product'),
                name='unique_product_per_sale'
            ),
        ]

    def clean(self) -> None:
        super().clean()

        if self.quantity <= 0:
            raise ValidationError(
                {'quantity': 'La cantidad debe ser mayor que 0.'}
            )

        if self.unit_price < 0:
            raise ValidationError(
                {'unit_price': 'El precio unitario no puede ser negativo.'}
            )

        if self.sale_id and self.sale.status != Sale.Status.DRAFT:  # type: ignore
            raise ValidationError(
                'No se pueden modificar los items de una venta '
                'que no está en estado borrador.'
            )

    @property
    def subtotal(self) -> Decimal:
        if self.quantity is None or self.unit_price is None:
            return Decimal('0')
        return self.quantity * self.unit_price

    def __str__(self) -> str:
        return f'{self.product} - {self.quantity}'