from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from products.models import Product
from suppliers.models import Supplier

from .models import Purchase, PurchaseItem


# Create your tests here.
User = get_user_model()


class PurchaseAPITests(TestCase):

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

        self.user.groups.add(
            self.group,
        )

        permissions = Permission.objects.filter(
            content_type__app_label='purchases',
            content_type__model__in=[
                'purchase',
                'purchaseitem',
            ],
            codename__in=[
                'add_purchase',
                'change_purchase',
                'view_purchase',
                'delete_purchase',
                'add_purchaseitem',
                'change_purchaseitem',
                'view_purchaseitem',
                'delete_purchaseitem',
            ],
        )

        self.group.permissions.set(
            permissions,
        )

        self.supplier = Supplier.objects.create(
            supplier_type=Supplier.SupplierType.PERSON,
            tax_id='20123456789',
            first_name='Pedro',
            last_name='Gómez',
            email='pedro@test.com',
        )

        self.product = Product.objects.create(
            name='Producto Test',
            sku='TEST-001',
            price='100.00',
            cost='50.00',
            stock='10.000',
        )

        self.purchase = Purchase.objects.create(
            supplier=self.supplier,
            reference='COMP-001',
        )

        self.url = '/api/purchases/'

    def authenticate(self):
        self.client.force_authenticate(  # type: ignore
            user=self.user,
        )

    def test_authenticated_user_can_list_purchases(self):
        self.authenticate()

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['results']),  # type: ignore
            1,
        )

    def test_unauthenticated_user_cannot_access_purchases(self):
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_retrieve_purchase(self):
        self.authenticate()

        response = self.client.get(
            f'{self.url}{self.purchase.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['id'],  # type: ignore
            self.purchase.pk,
        )

        self.assertEqual(
            response.data['supplier'],  # type: ignore
            self.supplier.pk,
        )

    def test_unauthenticated_user_cannot_retrieve_purchase(self):
        response = self.client.get(
            f'{self.url}{self.purchase.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_create_purchase(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                'supplier': self.supplier.pk,
                'reference': 'COMP-002',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Purchase.objects.filter(
                reference='COMP-002',
            ).exists()
        )

    def test_user_can_update_draft_purchase(self):
        self.authenticate()

        response = self.client.patch(
            f'{self.url}{self.purchase.pk}/',
            {
                'reference': 'COMP-UPDATED',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.reference,
            'COMP-UPDATED',
        )

    def test_user_can_delete_draft_purchase(self):
        self.authenticate()

        response = self.client.delete(
            f'{self.url}{self.purchase.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Purchase.objects.filter(
                pk=self.purchase.pk,
            ).exists()
        )

    def test_user_can_create_purchase_item(self):
        self.authenticate()

        response = self.client.post(
            '/api/purchase-items/',
            {
                'purchase': self.purchase.pk,
                'product': self.product.pk,
                'quantity': '2.000',
                'unit_cost': '50.00',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            PurchaseItem.objects.filter(
                purchase=self.purchase,
                product=self.product,
            ).exists()
        )

    def test_user_can_update_purchase_item_in_draft_purchase(self):
        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal('2.000'),
            unit_cost=Decimal('50.00'),
        )

        self.authenticate()

        response = self.client.patch(
            f'/api/purchase-items/{item.pk}/',
            {
                'quantity': '3.000',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        item.refresh_from_db()

        self.assertEqual(
            item.quantity,
            Decimal('3.000'),
        )

    def test_user_can_delete_purchase_item_in_draft_purchase(self):
        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal('2.000'),
            unit_cost=Decimal('50.00'),
        )

        self.authenticate()

        response = self.client.delete(
            f'/api/purchase-items/{item.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            PurchaseItem.objects.filter(
                pk=item.pk,
            ).exists()
        )

    def test_user_cannot_create_purchase_item_with_invalid_quantity(self):
        self.authenticate()

        response = self.client.post(
            '/api/purchase-items/',
            {
                'purchase': self.purchase.pk,
                'product': self.product.pk,
                'quantity': '0.000',
                'unit_cost': '50.00',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_cannot_create_purchase_item_with_negative_unit_cost(self):
        self.authenticate()

        response = self.client.post(
            '/api/purchase-items/',
            {
                'purchase': self.purchase.pk,
                'product': self.product.pk,
                'quantity': '2.000',
                'unit_cost': '-1.00',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_purchase_item_subtotal_is_calculated(self):
        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal('3.000'),
            unit_cost=Decimal('50.00'),
        )

        self.assertEqual(
            item.subtotal,
            Decimal('150.000'),
        )

    def test_cannot_add_duplicate_product_to_purchase(self):
        PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal('2.000'),
            unit_cost=Decimal('50.00'),
        )

        self.authenticate()

        response = self.client.post(
            '/api/purchase-items/',
            {
                'purchase': self.purchase.pk,
                'product': self.product.pk,
                'quantity': '3.000',
                'unit_cost': '50.00',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_cannot_update_confirmed_purchase(self):
        self.purchase.status = Purchase.Status.CONFIRMED
        self.purchase.save()

        self.authenticate()

        response = self.client.patch(
            f'{self.url}{self.purchase.pk}/',
            {
                'reference': 'NO-DEBE-CAMBIAR',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.purchase.refresh_from_db()

        self.assertNotEqual(
            self.purchase.reference,
            'NO-DEBE-CAMBIAR',
        )

    def test_user_cannot_delete_confirmed_purchase(self):
        self.purchase.status = Purchase.Status.CONFIRMED
        self.purchase.save()

        self.authenticate()

        response = self.client.delete(
            f'{self.url}{self.purchase.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertTrue(
            Purchase.objects.filter(
                pk=self.purchase.pk,
            ).exists()
        )

    def test_user_cannot_add_item_to_confirmed_purchase(self):
        self.purchase.status = Purchase.Status.CONFIRMED
        self.purchase.save()

        self.authenticate()

        response = self.client.post(
            '/api/purchase-items/',
            {
                'purchase': self.purchase.pk,
                'product': self.product.pk,
                'quantity': '2.000',
                'unit_cost': '50.00',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_cannot_update_item_of_confirmed_purchase(self):
        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal('2.000'),
            unit_cost=Decimal('50.00'),
        )

        self.purchase.status = Purchase.Status.CONFIRMED
        self.purchase.save()

        self.authenticate()

        response = self.client.patch(
            f'/api/purchase-items/{item.pk}/',
            {
                'quantity': '3.000',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        item.refresh_from_db()

        self.assertEqual(
            item.quantity,
            Decimal('2.000'),
        )

    def test_user_cannot_delete_item_of_confirmed_purchase(self):
        item = PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal('2.000'),
            unit_cost=Decimal('50.00'),
        )

        self.purchase.status = Purchase.Status.CONFIRMED
        self.purchase.save()

        self.authenticate()

        response = self.client.delete(
            f'/api/purchase-items/{item.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertTrue(
            PurchaseItem.objects.filter(
                pk=item.pk,
            ).exists()
        )

    def test_user_cannot_confirm_purchase(self):
        PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal('5.000'),
            unit_cost=Decimal('100.00'),
        )

        self.authenticate()

        response = self.client.post(
            f'{self.url}{self.purchase.pk}/confirm/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            Purchase.Status.DRAFT,
        )

    def test_admin_can_confirm_purchase_and_increase_stock(self):
        PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal('5.000'),
            unit_cost=Decimal('100.00'),
        )

        self.product.stock = Decimal('10.000')
        self.product.save()

        admin = User.objects.create_superuser(
            email='admin@test.com',
            password='password123',
            first_name='Admin',
            last_name='Test',
        ) # type: ignore

        self.client.force_authenticate( # type: ignore
            user=admin,
        )

        response = self.client.post(
            f'{self.url}{self.purchase.pk}/confirm/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.purchase.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            Purchase.Status.CONFIRMED,
        )

        self.assertIsNotNone(
            self.purchase.confirmed_at,
        )

        self.assertEqual(
            self.product.stock,
            Decimal('15.000'),
        )

    def test_admin_cannot_confirm_purchase_without_items(self):
        admin = User.objects.create_superuser(
            email='admin@test.com',
            password='password123',
            first_name='Admin',
            last_name='Test',
        ) # type: ignore

        self.client.force_authenticate( # type: ignore
            user=admin,
        )

        response = self.client.post(
            f'{self.url}{self.purchase.pk}/confirm/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            Purchase.Status.DRAFT,
        )

    def test_admin_cannot_confirm_already_confirmed_purchase(self):
        PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal('5.000'),
            unit_cost=Decimal('100.00'),
        )

        admin = User.objects.create_superuser(
            email='admin@test.com',
            password='password123',
            first_name='Admin',
            last_name='Test',
        ) # type: ignore

        self.client.force_authenticate( # type: ignore
            user=admin,
        )

        first_response = self.client.post(
            f'{self.url}{self.purchase.pk}/confirm/',
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        self.product.refresh_from_db()

        stock_after_first_confirmation = self.product.stock

        second_response = self.client.post(
            f'{self.url}{self.purchase.pk}/confirm/',
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            stock_after_first_confirmation,
        )

    def test_admin_can_cancel_confirmed_purchase_and_decrease_stock(self):
        PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal('5.000'),
            unit_cost=Decimal('100.00'),
        )

        self.product.stock = Decimal('10.000')
        self.product.save()

        admin = User.objects.create_superuser(
            email='admin@test.com',
            password='password123',
            first_name='Admin',
            last_name='Test',
        ) # type: ignore

        self.client.force_authenticate( # type: ignore
            user=admin,
        )

        confirm_response = self.client.post(
            f'{self.url}{self.purchase.pk}/confirm/',
        )

        self.assertEqual(
            confirm_response.status_code,
            status.HTTP_200_OK,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            Decimal('15.000'),
        )

        cancel_response = self.client.post(
            f'{self.url}{self.purchase.pk}/cancel/',
        )

        self.assertEqual(
            cancel_response.status_code,
            status.HTTP_200_OK,
        )

        self.purchase.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            Purchase.Status.CANCELLED,
        )

        self.assertEqual(
            self.product.stock,
            Decimal('10.000'),
        )

    def test_user_cannot_cancel_purchase(self):
        PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal('5.000'),
            unit_cost=Decimal('100.00'),
        )

        admin = User.objects.create_superuser(
            email='admin@test.com',
            password='password123',
            first_name='Admin',
            last_name='Test',
        ) # type: ignore

        self.client.force_authenticate( # type: ignore
            user=admin,
        )

        response = self.client.post(
            f'{self.url}{self.purchase.pk}/confirm/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.client.force_authenticate( # type: ignore
            user=self.user,
        )

        response = self.client.post(
            f'{self.url}{self.purchase.pk}/cancel/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            Purchase.Status.CONFIRMED,
        )

    def test_admin_cannot_cancel_draft_purchase(self):
        admin = User.objects.create_superuser(
            email='admin@test.com',
            password='password123',
            first_name='Admin',
            last_name='Test',
        ) # type: ignore

        self.client.force_authenticate( # type: ignore
            user=admin,
        )

        response = self.client.post(
            f'{self.url}{self.purchase.pk}/cancel/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            Purchase.Status.DRAFT,
        )

    def test_admin_cannot_cancel_purchase_if_stock_would_be_negative(self):
        PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal('5.000'),
            unit_cost=Decimal('100.00'),
        )

        self.product.stock = Decimal('0.000')
        self.product.save()

        admin = User.objects.create_superuser(
            email='admin@test.com',
            password='password123',
            first_name='Admin',
            last_name='Test',
        ) # type: ignore

        self.client.force_authenticate( # type: ignore
            user=admin,
        )

        confirm_response = self.client.post(
            f'{self.url}{self.purchase.pk}/confirm/',
        )

        self.assertEqual(
            confirm_response.status_code,
            status.HTTP_200_OK,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            Decimal('5.000'),
        )

        # Simulamos que parte del stock fue vendido/utilizado.
        self.product.stock = Decimal('3.000')
        self.product.save()

        cancel_response = self.client.post(
            f'{self.url}{self.purchase.pk}/cancel/',
        )

        self.assertEqual(
            cancel_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.purchase.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            Purchase.Status.CONFIRMED,
        )

        self.assertEqual(
            self.product.stock,
            Decimal('3.000'),
        )