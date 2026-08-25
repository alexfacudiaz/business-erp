from django.db import models
from django.core.exceptions import ValidationError

from core.models import TimeStampedModel

# Create your models here.
class Customer(TimeStampedModel):

    class CustomerType(models.TextChoices):
        PERSON = 'PERSON', 'Persona'
        COMPANY = 'COMPANY', 'Empresa'

    customer_type = models.CharField(
        max_length=7,
        choices=CustomerType.choices
    )

    tax_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    business_name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        permissions = [
            ('deactivate_customer', 'Can deactivate customer'),
            ('activate_customer', 'Can activate customer'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    (
                        models.Q(customer_type='PERSON')
                        & models.Q(first_name__isnull=False)
                        & models.Q(last_name__isnull=False)
                        & models.Q(business_name__isnull=True)
                    )
                    |
                    (
                        models.Q(customer_type='COMPANY')
                        & models.Q(business_name__isnull=False)
                        & models.Q(first_name__isnull=True)
                        & models.Q(last_name__isnull=True)
                    )
                ),
                name='valid_customer_type_data'
            ),
        ]

    def clean(self) -> None:
        super().clean()

        if self.customer_type == self.CustomerType.PERSON:
            if not self.first_name:
                raise ValidationError(
                    {"first_name": "Las personas deben tener nombre."}
                )

            if not self.last_name:
                raise ValidationError(
                    {"last_name": "Las personas deben tener apellido."}
                )

            if self.business_name:
                raise ValidationError(
                    {"business_name": "Las personas no deben tener razón social."}
                )

        elif self.customer_type == self.CustomerType.COMPANY:
            if not self.business_name:
                raise ValidationError(
                    {"business_name": "Las empresas deben tener razón social."}
                )

            if self.first_name or self.last_name:
                raise ValidationError(
                    {
                        "first_name": (
                            "Las empresas no deben tener nombre o apellido."
                        ),
                        "last_name": (
                            "Las empresas no deben tener nombre o apellido."
                        ),
                    }
                )

    def __str__(self) -> str:
        if self.customer_type == self.CustomerType.PERSON:
            return f'{self.first_name} {self.last_name}'
        return f'{self.business_name}'