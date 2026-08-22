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

