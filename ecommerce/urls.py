"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from store import views

urlpatterns = [
    
    path("admin/", admin.site.urls),

    # products URLs
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    
    # auth URLs
    path('register/', views.UserRegistrationView.as_view(), name='user-registration'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutView.as_view(), name='user-logout'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('password/reset/', views.CustomPasswordResetView.as_view(), name='password-reset'),
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='password-change'),
    
    # cart URLs
    path('cart/', views.CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/<int:product_id>/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/<int:product_id>/', views.RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/update/<int:product_id>/', views.UpdateCartItemView.as_view(), name='update-cart-item'),
    
    # order URLs
    path('order/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('order/<int:order_id>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('order/history/', views.OrderHistoryView.as_view(), name='order-history'),
    
    # payment URLs
    path('payment/initiate/', views.PaymentInitiateView.as_view(), name='payment-initiate'),
    path('payment/confirm/', views.PaymentConfirmView.as_view(), name='payment-confirm'),
    path('payment/cancel/', views.PaymentCancelView.as_view(), name='payment-cancel'),
    
    #API URLs if needed
]
