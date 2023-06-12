from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView, PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Product, Order, OrderItem, Cart, CartItem
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

###########################Product action views######################
class ProductListView(View):
    def get(self, request):
        products = Product.objects.all()
        data = [{'id': product.id, 'name': product.name} for product in products]
        return JsonResponse(data, safe=False)

class ProductDetailView(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        data = {'id': product.id, 'name': product.name, 'price': product.price}
        return JsonResponse(data)

class ProductCreateView(View):
    def post(self, request):
        data = request.POST or request.data

        name = data.get('name')
        price = data.get('price')

        if not name or not price:
            return JsonResponse({'error': 'Name and price are required fields.'}, status=400)

        try:
            price = float(price)
        except ValueError:
            return JsonResponse({'error': 'Price must be a valid number.'}, status=400)

        product = Product(name=name, price=price)
        product.save()

        return JsonResponse({'success': 'Product created successfully.'})

class ProductUpdateView(View):
    def put(self, request, pk):
        data = request.PUT or request.data

        product = get_object_or_404(Product, pk=pk)

        name = data.get('name')
        price = data.get('price')

        if name:
            product.name = name

        if price:
            try:
                price = float(price)
            except ValueError:
                return JsonResponse({'error': 'Price must be a valid number.'}, status=400)

            product.price = price

        product.save()

        return JsonResponse({'success': 'Product updated successfully.'})

class ProductDeleteView(View):
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return JsonResponse({'success': 'Product deleted successfully.'})


####################Customer action views###########################

class UserRegistrationView(View):
    @csrf_protect
    def post(self, request):
        data = request.POST or request.data

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Username and password are required fields.'}, status=400)

        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username is already taken.'}, status=400)

        try:
            # Validate the password strength
            validate_password(password)

            # Additional validation and checks can be performed here if needed

            # Create the user
            user = User.objects.create_user(username=username, password=password)
            login(request, user)

            return JsonResponse({'success': 'User registered and logged in successfully.'})
        except ValidationError as e:
            return JsonResponse({'error': e.messages}, status=400)

class UserLoginView(View):
    @csrf_protect
    def post(self, request):
        data = request.POST or request.data

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Username and password are required fields.'}, status=400)

        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse({'error': 'Invalid credentials.'}, status=401)

        login(request, user)

        return JsonResponse({'success': 'User logged in successfully.'})

class UserLogoutView(LoginRequiredMixin, View):
    @csrf_protect
    def post(self, request):
        logout(request)
        return JsonResponse({'success': 'User logged out successfully.'})

class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        data = {'username': user.username, 'email': user.email}  # Customize the data as per your needs
        return JsonResponse(data)

class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.html'  # Customize the email template path
    success_url = reverse_lazy('password-reset-done')  # Customize the success URL path

class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('password-change-done')  # Customize the success URL path

################################Cart Action views###############################

class CartDetailView(View):
    def get(self, request):
        # Get the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()

        # Serialize cart items
        data = [{'id': item.id, 'product': item.product.name, 'quantity': item.quantity} for item in cart_items]
        return JsonResponse(data, safe=False)

class AddToCartView(View):
    def post(self, request, product_id):
        # Get the product
        product = get_object_or_404(Product, id=product_id)

        # Get the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if the product is already in the cart
        cart_item, item_created = cart.items.get_or_create(product=product)

        # Increase the quantity if the item already exists, or create a new item with quantity 1
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({'success': 'Product added to cart successfully.'})

class RemoveFromCartView(View):
    def post(self, request, product_id):
        # Get the product
        product = get_object_or_404(Product, id=product_id)

        # Get the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if the product is in the cart
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)

        # Decrease the quantity or remove the item if the quantity becomes zero
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

        return JsonResponse({'success': 'Product removed from cart successfully.'})

class UpdateCartItemView(View):
    def post(self, request, product_id):
        # Get the product
        product = get_object_or_404(Product, id=product_id)

        # Get the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if the product is in the cart
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)

        # Update the quantity based on the request data
        quantity = int(request.POST.get('quantity', 0))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()

        return JsonResponse({'success': 'Cart item updated successfully.'})

####################### Order views ########################################

class OrderCreateView(LoginRequiredMixin, View):
    @csrf_protect
    def post(self, request):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        # Create an order based on the items in the user's cart
        order = Order.objects.create(user=user)
        for item in cart.items.all():
            # Create an order item for each item in the cart
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        # Clear the user's cart
        cart.items.all().delete()
        return JsonResponse({'message': 'Order created successfully'})

class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order_items = order.items.all()
        data = {
            'order_id': order.id,
            'total_price': order.total_price(),
            'items': [{'product': item.product.name, 'quantity': item.quantity} for item in order_items]
        }
        return JsonResponse(data)

class OrderHistoryView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        data = []
        for order in orders:
            order_items = order.items.all()
            data.append({
                'order_id': order.id,
                'total_price': order.total_price(),
                'items': [{'product': item.product.name, 'quantity': item.quantity} for item in order_items]
            })
        return JsonResponse(data, safe=False)

####################### Payment views ########################################

class PaymentInitiateView(View):
    def post(self, request):
        # Retrieve the cart items and calculate the total price
        cart = request.session.get('cart', {})
        total_price = sum(item['price'] * item['quantity'] for item in cart.values())

        # Store the total price in the session
        request.session['total_price'] = total_price

        # Set payment status to initiated
        request.session['payment_status'] = 'initiated'

        messages.success(request, "Payment initiated successfully.")
        return redirect('payment-confirm')

class PaymentConfirmView(View):
    def get(self, request):
        # Check if payment status is initiated
        if request.session.get('payment_status') == 'initiated':
            # Simulate payment confirmation
            # Update the order status or perform any necessary actions
            # ...

            # Clear the cart and payment-related session data
            request.session['cart'] = {}
            request.session['total_price'] = None
            request.session['payment_status'] = None

            messages.success(request, "Payment confirmed successfully.")
            return redirect('order-history')
        else:
            messages.error(request, "Invalid payment confirmation.")
            return redirect('cart-detail')

class PaymentCancelView(View):
    def get(self, request):
        # Check if payment status is initiated
        if request.session.get('payment_status') == 'initiated':
            # Clear the cart and payment-related session data
            request.session['cart'] = {}
            request.session['total_price'] = None
            request.session['payment_status'] = None

            messages.warning(request, "Payment cancelled.")
            return redirect('cart-detail')
        else:
            messages.error(request, "Invalid payment cancellation.")
            return redirect('cart-detail')
