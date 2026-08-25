from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Product


# Create your tests here.
User = get_user_model()


class ProductAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='usuario@test.com',
            password='password123',
            first_name='Juan',
            last_name='Pérez',
        )  # type: ignore

        self.group = Group.objects.create(
            name='USUARIO',
        )

        self.user.groups.add(self.group)

        permissions = Permission.objects.filter(
            content_type__app_label='products',
            content_type__model='product',
            codename='view_product',
        )

        self.group.permissions.set(permissions)

        self.product = Product.objects.create(
            name='Producto Test',
            sku='SKU-001',
            description='Producto de prueba',
            price='100.00',
            cost='60.00',
            stock='25.000',
            min_stock='5.000',
        )

        self.url = '/api/products/'

    def authenticate(self):
        self.client.force_authenticate( # type: ignore
            user=self.user,
        )

    def test_authenticated_user_can_list_products(self):
        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['results']),  # type: ignore
            1,
        )

    def test_authenticated_user_can_retrieve_product(self):
        self.authenticate()

        response = self.client.get(
            f'{self.url}{self.product.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['id'],  # type: ignore
            self.product.pk,
        )

    def test_unauthenticated_user_cannot_access_products(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_cannot_create_product(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                'name': 'Nuevo Producto',
                'sku': 'SKU-002',
                'description': 'Producto nuevo',
                'price': '200.00',
                'cost': '120.00',
                'min_stock': '10.000',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            Product.objects.filter(
                sku='SKU-002',
            ).exists()
        )

    def test_user_cannot_update_product(self):
        self.authenticate()

        response = self.client.patch(
            f'{self.url}{self.product.pk}/',
            {
                'name': 'Producto Modificado',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.name,
            'Producto Test',
        )

    def test_user_cannot_delete_product(self):
        self.authenticate()

        response = self.client.delete(
            f'{self.url}{self.product.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Product.objects.filter(
                pk=self.product.pk,
            ).exists()
        )

    def test_can_filter_products_by_sku(self):
        Product.objects.create(
            name='Otro Producto',
            sku='SKU-002',
            price='200.00',
            cost='120.00',
            stock='10.000',
            min_stock='2.000',
        )

        self.authenticate()

        response = self.client.get(
            self.url,
            {'sku': 'SKU-002'},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['results']),  # type: ignore
            1,
        )

        self.assertEqual(
            response.data['results'][0]['sku'],  # type: ignore
            'SKU-002',
        )

    def test_can_search_products(self):
        self.authenticate()

        response = self.client.get(
            self.url,
            {'search': 'Producto Test'},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['results']),  # type: ignore
            1,
        )

        self.assertEqual(
            response.data['results'][0]['name'],  # type: ignore
            'Producto Test',
        )

    def test_can_order_products_by_price(self):
        Product.objects.create(
            name='Producto Barato',
            sku='SKU-002',
            price='50.00',
            cost='30.00',
            stock='10.000',
            min_stock='2.000',
        )

        self.authenticate()

        response = self.client.get(
            self.url,
            {'ordering': 'price'},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['results'][0]['sku'],  # type: ignore
            'SKU-002',
        )

    def test_stock_cannot_be_modified_through_api(self):
        permission = Permission.objects.get(
            content_type__app_label='products',
            content_type__model='product',
            codename='change_product',
        )

        self.group.permissions.add(permission)

        self.authenticate()

        response = self.client.patch(
            f'{self.url}{self.product.pk}/',
            {
                'stock': '999.000',
                'name': 'Producto Modificado',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            Decimal('25.000'),
        )

        self.assertEqual(
            self.product.name,
            'Producto Modificado',
        )

    def test_stock_cannot_be_set_when_creating_product(self):
        permission = Permission.objects.get(
            content_type__app_label='products',
            content_type__model='product',
            codename='add_product',
        )

        self.group.permissions.add(permission)

        self.authenticate()

        response = self.client.post(
            self.url,
            {
                'name': 'Producto Nuevo',
                'sku': 'SKU-002',
                'price': '200.00',
                'cost': '120.00',
                'stock': '999.000',
                'min_stock': '10.000',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        product = Product.objects.get(
            sku='SKU-002',
        )

        self.assertEqual(
            product.stock,
            Decimal('0.000'),
        )

    def test_user_with_change_permission_can_update_product(self):
        permission = Permission.objects.get(
            content_type__app_label='products',
            content_type__model='product',
            codename='change_product',
        )

        self.group.permissions.add(permission)

        self.authenticate()

        response = self.client.patch(
            f'{self.url}{self.product.pk}/',
            {
                'name': 'Producto Actualizado',
                'price': '150.00',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.name,
            'Producto Actualizado',
        )

        self.assertEqual(
            self.product.price,
            Decimal('150.00'),
        )