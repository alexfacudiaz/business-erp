from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from customers.models import Customer
from products.models import Product
from .models import Sale, SaleItem
from .services import cancel_sale, confirm_sale

# Create your tests here.
class SaleServiceTests(TestCase):

    def setUp(self) -> None:
        self.customer = Customer.objects.create(
            customer_type=Customer.CustomerType.PERSON,
            first_name='Juan',
            last_name='Perez',
        )

        self.product = Product.objects.create(
            name='Producto de prueba',
            sku='TEST-001',
            price=Decimal('100.00'),
            cost=Decimal('50.00'),
            stock=Decimal('10.000'),
            min_stock=Decimal('2.000'),
        )

        self.sale = Sale.objects.create(
            customer=self.customer,
            status=Sale.Status.DRAFT,
        )

    def create_item(
            self,
            sale=None,
            product=None,
            quantity=Decimal('2.000'),
            unit_price=Decimal('100.00'),
    ):
        return SaleItem.objects.create(
            sale=sale or self.sale,
            product=product or self.product,
            quantity=quantity,
            unit_price=unit_price,
        )

    def test_confirm_sale_changes_status(self):
        self.create_item()

        confirm_sale(self.sale)

        self.sale.refresh_from_db()

        self.assertEqual(
            self.sale.status,
            Sale.Status.CONFIRMED,
        )

        self.assertIsNotNone(
            self.sale.confirmed_at,
        )

    def test_confirm_sale_decreases_stock(self):
        self.create_item(
            quantity=Decimal('3.000'),
        )

        confirm_sale(self.sale)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            Decimal('7.000'),
        )

    def test_confirm_sale_without_items_fails(self):
        with self.assertRaisesMessage(
            ValidationError,
            'No se puede confirmar una venta sin productos.',
        ):
            confirm_sale(self.sale)

        self.sale.refresh_from_db()

        self.assertEqual(
            self.sale.status,
            Sale.Status.DRAFT,
        )

    def test_confirm_sale_non_draft_fails(self):
        self.sale.status = Sale.Status.CONFIRMED
        self.sale.save()

        self.create_item()

        with self.assertRaisesMessage(
            ValidationError,
            'Solo se pueden confirmar ventas en estado borrador.',
        ):
            confirm_sale(self.sale)

    def test_confirm_sale_without_enough_stock_fails(self):
        self.create_item(
            quantity=Decimal('11.000'),
        )

        with self.assertRaisesMessage(
            ValidationError,
            'No hay stock suficiente para el producto',
        ):
            confirm_sale(self.sale)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            Decimal('10.000'),
        )

        self.sale.refresh_from_db()

        self.assertEqual(
            self.sale.status,
            Sale.Status.DRAFT,
        )

    def test_confirm_sale_rolls_back_previous_stock_changes(self):
        second_product = Product.objects.create(
            name='Segundo producto',
            sku='TEST-002',
            price=Decimal('200.00'),
            cost=Decimal('100.00'),
            stock=Decimal('2.000'),
            min_stock=Decimal('1.000'),
        )

        self.create_item(
            product=self.product,
            quantity=Decimal('5.000'),
        )

        self.create_item(
            product=second_product,
            quantity=Decimal('3.000'),
        )

        with self.assertRaises(ValidationError):
            confirm_sale(self.sale)

        self.product.refresh_from_db()
        second_product.refresh_from_db()
        self.sale.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            Decimal('10.000'),
        )

        self.assertEqual(
            second_product.stock,
            Decimal('2.000'),
        )

        self.assertEqual(
            self.sale.status,
            Sale.Status.DRAFT,
        )

    def test_cancel_sale_restores_stock(self):
        self.create_item(
            quantity=Decimal('3.000'),
        )

        confirm_sale(self.sale)

        cancel_sale(self.sale)

        self.product.refresh_from_db()
        self.sale.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            Decimal('10.000'),
        )

        self.assertEqual(
            self.sale.status,
            Sale.Status.CANCELLED,
        )

    def test_cancel_sale_requires_confirmed_status(self):
        self.create_item()

        with self.assertRaisesMessage(
            ValidationError,
            'Solo se pueden cancelar ventas confirmadas.',
        ):
            cancel_sale(self.sale)

    def test_cancel_cancelled_sale_fails(self):
        self.sale.status = Sale.Status.CANCELLED
        self.sale.save()

        with self.assertRaisesMessage(
            ValidationError,
            'Solo se pueden cancelar ventas confirmadas.',
        ):
            cancel_sale(self.sale)


from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import status
from rest_framework.test import APIClient


User = get_user_model()


class SaleAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='usuario@test.com',
            password='password123',
            first_name='Juan',
            last_name='Pérez',
        ) # type: ignore

        self.group = Group.objects.create(
            name='USUARIO',
        )

        permissions = Permission.objects.filter(
            content_type__app_label='sales',
            codename__in=[
                'add_sale',
                'change_sale',
                'view_sale',
                'confirm_sale',
                'add_saleitem',
                'change_saleitem',
                'delete_saleitem',
                'view_saleitem',
            ],
        )

        self.group.permissions.set(permissions)
        self.user.groups.add(self.group)

        self.customer = Customer.objects.create(
            customer_type=Customer.CustomerType.PERSON,
            first_name='Carlos',
            last_name='Gómez',
        )

        self.product = Product.objects.create(
            name='Producto API',
            sku='API-001',
            price=Decimal('100.00'),
            cost=Decimal('50.00'),
            stock=Decimal('10.000'),
            min_stock=Decimal('2.000'),
        )

        self.sale = Sale.objects.create(
            customer=self.customer,
            status=Sale.Status.DRAFT,
        )

        self.sale_url = f'/api/sales/{self.sale.pk}/'
        self.confirm_url = f'/api/sales/{self.sale.pk}/confirm/'
        self.cancel_url = f'/api/sales/{self.sale.pk}/cancel/'

    def authenticate(self):
        self.client.force_authenticate( # type: ignore
            user=self.user,
        )

    def create_item(self, quantity=Decimal('2.000')):
        return SaleItem.objects.create(
            sale=self.sale,
            product=self.product,
            quantity=quantity,
            unit_price=Decimal('100.00'),
        )

    def test_authenticated_user_can_list_sales(self):
        self.authenticate()

        response = self.client.get('/api/sales/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_user_can_confirm_sale(self):
        self.authenticate()
        self.create_item()

        response = self.client.post(
            self.confirm_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.sale.refresh_from_db()

        self.assertEqual(
            self.sale.status,
            Sale.Status.CONFIRMED,
        )

    def test_user_cannot_cancel_sale(self):
        self.authenticate()
        self.create_item()

        confirm_sale(self.sale)

        response = self.client.post(
            self.cancel_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.sale.refresh_from_db()

        self.assertEqual(
            self.sale.status,
            Sale.Status.CONFIRMED,
        )

    def test_confirm_sale_without_items_returns_400(self):
        self.authenticate()

        response = self.client.post(
            self.confirm_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.sale.refresh_from_db()

        self.assertEqual(
            self.sale.status,
            Sale.Status.DRAFT,
        )

    def test_user_can_delete_sale_item_in_draft(self):
        self.authenticate()

        item = self.create_item()

        response = self.client.delete(
            f'/api/sale-items/{item.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            SaleItem.objects.filter(pk=item.pk).exists(),
        )

    def test_user_cannot_modify_confirmed_sale(self):
        self.authenticate()
        self.create_item()

        confirm_sale(self.sale)

        response = self.client.patch(
            self.sale_url,
            {
                'reference': 'MODIFICADA',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_cannot_delete_confirmed_sale(self):
        self.authenticate()
        self.create_item()

        confirm_sale(self.sale)

        response = self.client.delete(
            self.sale_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_user_cannot_modify_item_of_confirmed_sale(self):
        self.authenticate()

        item = self.create_item()

        confirm_sale(self.sale)

        response = self.client.patch(
            f'/api/sale-items/{item.pk}/',
            {
                'quantity': '3.000',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_unauthenticated_user_cannot_access_sales(self):
        response = self.client.get('/api/sales/')

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )