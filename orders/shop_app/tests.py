from django.test import TestCase, Client
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import Product, Order, Shop

User = get_user_model()

class RegisterBuyerViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_buyer(self):
        url = reverse('register')
        data = {
            'email': 'buyer@example.com',
            'username': 'buyer',
            'password': 'password123',
            'type': 'buyer'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ConfirmEmailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='buyer@example.com', username='buyer', password='password123')

    def test_confirm_email(self):
        token = Token.objects.create(user=self.user)
        url = reverse('confirm-email')
        data = {
            'key': token.key
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='buyer@example.com', username='buyer', password='password123')

    def test_login(self):
        url = reverse('login')
        data = {
            'email': 'buyer@example.com',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserProfileViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='buyer@example.com', username='buyer', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_user_profile(self):
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProductSearchViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_search_products(self):
        url = reverse('search')
        response = self.client.get(url, {'query': 'product'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CartViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='buyer@example.com', username='buyer', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_cart(self):
        url = reverse('cart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateShopViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='shop@example.com', username='shop', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_shop(self):
        url = reverse('create-shop')
        data = {
            'name': 'Shop 1',
            'url': 'http://example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UpdatePriceViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='shop@example.com', username='shop', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_update_price(self):
        shop = Shop.objects.create(name='Shop 1', user=self.user)
        product = Product.objects.create(name='Product 1')
        url = reverse('update-price')
        data = {
            'shop_id': shop.pk,
            'product_infos': [
                {'id': product.pk, 'price': 100}
            ]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ShopStatusViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='shop@example.com', username='shop', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_update_shop_status(self):
        url = reverse('shop-status')
        data = {
            'is_active': False
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ShopUpdateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='shop@example.com', username='shop', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.shop = Shop.objects.create(name="Shop 1", url="http://example.com")

    def test_update_shop(self):
        url = reverse('shop-update')
        data = {
            'shop_id': self.shop.id,
            'name': 'Updated Shop'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ShopOrdersViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='shop@example.com', username='shop', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_shop_orders(self):
        url = reverse('shop-orders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ContactViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='buyer@example.com', username='buyer', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_contacts(self):
        url = reverse('contacts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserOrdersViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='buyer@example.com', username='buyer', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_user_orders(self):
        url = reverse('user-orders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)