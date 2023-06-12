from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product, Cart, CartItem, Order, OrderItem
from django.contrib.auth.hashers import make_password

################## Products tests#################
class ProductViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.product = Product.objects.create(name='Test Product', price=10.99)

    def test_product_list_view(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)  # Assuming there is only one product in the database

    def test_product_detail_view(self):
        url = reverse('product-detail', args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.product.id)
        self.assertEqual(response.json()['name'], self.product.name)
        self.assertEqual(response.json()['price'], self.product.price)

    def test_product_create_view(self):
        url = reverse('product-create')
        data = {
            'name': 'New Product',
            'price': 19.99
        }
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Product.objects.filter(name='New Product').exists())

    def test_product_update_view(self):
        url = reverse('product-update', args=[self.product.id])
        data = {
            'name': 'Updated Product',
            'price': 15.99
        }
        self.client.login(username='testuser', password='testpass')
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')
        self.assertEqual(self.product.price, 15.99)

    def test_product_delete_view(self):
        url = reverse('product-delete', args=[self.product.id])
        self.client.login(username='testuser', password='testpass')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

######################### Auth for customer tests#############


class CustomerViewsTestCase(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create(username=self.username, password=make_password(self.password))

    def test_user_registration_view(self):
        url = reverse('user-registration')
        data = {
            'username': 'newuser',
            'password': 'newpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the expected response

    def test_user_login_view(self):
        url = reverse('user-login')
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the expected response

    def test_user_logout_view(self):
        url = reverse('user-logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the expected response

    def test_user_profile_view(self):
        url = reverse('user-profile')
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the expected response

    def test_custom_password_reset_view(self):
        url = reverse('password-reset')
        data = {
            'email': 'testuser@example.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        # Add more assertions to check the expected response

    def test_custom_password_change_view(self):
        url = reverse('password-change')
        data = {
            'old_password': self.password,
            'new_password1': 'newpassword',
            'new_password2': 'newpassword'
        }
        self.client.force_login(self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        # Add more assertions to check the expected response

#####################Cart tests###############################

class CartViewsTestCase(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create(username=self.username, password=self.password)
        self.product = Product.objects.create(name='Test Product', price=10.99)

    def test_cart_detail_view(self):
        url = reverse('cart-detail')
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the expected response

    def test_add_to_cart_view(self):
        url = reverse('add-to-cart', args=[self.product.id])
        self.client.force_login(self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the expected response

    def test_remove_from_cart_view(self):
        url = reverse('remove-from-cart', args=[self.product.id])
        self.client.force_login(self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the expected response

    def test_update_cart_item_view(self):
        url = reverse('update-cart-item', args=[self.product.id])
        self.client.force_login(self.user)
        data = {
            'quantity': 3
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the expected response

###########################Order tests #############################
class OrderViewsTestCase(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create(username=self.username, password=self.password)
        self.product = Product.objects.create(name='Test Product', price=10.99)
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_order_create_view(self):
        url = reverse('order-create')
        self.client.force_login(self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the expected response

    def test_order_detail_view(self):
        order = Order.objects.create(user=self.user)
        order_item = OrderItem.objects.create(order=order, product=self.product, quantity=1)
        url = reverse('order-detail', args=[order.id])
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the expected response

    def test_order_history_view(self):
        order = Order.objects.create(user=self.user)
        order_item = OrderItem.objects.create(order=order, product=self.product, quantity=1)
        url = reverse('order-history')
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the expected response

################# Payment Test###################################

class PaymentViewsTestCase(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create(username=self.username, password=self.password)
        self.cart = Cart.objects.create(user=self.user)

    def test_payment_initiate_view(self):
        url = reverse('payment-initiate')
        self.client.force_login(self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        # Add more assertions to check the expected behavior

    def test_payment_confirm_view(self):
        self.client.force_login(self.user)
        self.client.session['payment_status'] = 'initiated'
        url = reverse('payment-confirm')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Add more assertions to check the expected behavior

    def test_payment_cancel_view(self):
        self.client.force_login(self.user)
        self.client.session['payment_status'] = 'initiated'
        url = reverse('payment-cancel')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Add more assertions to check the expected behavior