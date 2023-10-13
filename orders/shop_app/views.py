import os
from django.contrib.auth import get_user_model, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from orders.settings import EMAIL_HOST_PASSWORD, EMAIL_HOST_USER
from .models import Product, Order, OrderItem, ProductInfo, Shop, Contact, ConfirmEmailToken
from .serializers import UserSerializer, ProductSerializer, OrderSerializer, \
    OrderItemSerializer, ProductInfoSerializer, ShopSerializer, ContactSerializer
User = get_user_model()
from django.core.mail import send_mail

class RegisterBuyerView(APIView):
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                email=serializer.validated_data['email'],
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
                type='buyer'
            )
            user.save()
            
            # Создание ключа подтверждения
            token = ConfirmEmailToken.objects.create(user=user)

            # Отправка сообщения с ключом подтверждения
            send_mail(
                'Подтверждение электронной почты',
                f'Ваш ключ подтверждения: {token.key}',
                EMAIL_HOST_USER,
                [user.email],
                auth_password=EMAIL_HOST_PASSWORD,
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConfirmEmailView(APIView):
    def post(self, request, format=None):
        key = request.data.get('key')
        try:
            token = ConfirmEmailToken.objects.get(key=key)
            user = token.user
            user.is_active = True
            user.save()
            return Response({"message": "Email confirmed successfully"}, status=status.HTTP_200_OK)
        except ConfirmEmailToken.DoesNotExist:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, format=None):
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductSearchView(APIView):
    def get(self, request, format=None):
        query = request.query_params.get('query', '')
        products = Product.objects.filter(name__icontains=query)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        order = Order.objects.filter(user=request.user, state='cart').first()
        if order:
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        else:
            return Response({"message": "Cart is empty"})

    def post(self, request, format=None):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        product = Product.objects.filter(id=product_id).first()
        if product:
            order = Order.objects.filter(user=request.user, state='cart').first()
            if not order:
                order = Order.objects.create(user=request.user, state='cart')
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
            return Response({"message": "Product added to cart"})
        else:
            return Response({"error": "Product not found"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        product_id = request.data.get('product_id')
        order = Order.objects.filter(user=request.user, state='cart').first()
        if order:
            item = OrderItem.objects.filter(order=order, product_id=product_id).first()
            if item:
                item.delete()
                return Response({"message": "Product removed from cart"})
            else:
                return Response({"error": "Product not in cart"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

class UpdatePriceView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        shop_id = request.data.get('shop_id')
        product_infos = request.data.get('product_infos', [])
        shop = Shop.objects.filter(id=shop_id).first()
        if shop:
            for product_info_data in product_infos:
                product_info = ProductInfo.objects.filter(id=product_info_data.get('id')).first()
                if product_info:
                    serializer = ProductInfoSerializer(product_info, data=product_info_data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Prices updated"})
        else:
            return Response({"error": "Shop not found"}, status=status.HTTP_400_BAD_REQUEST)

class ShopStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        user = request.user
        if user.type == 'shop':
            user.is_active = request.data.get('is_active')
            user.save()
            return Response({"message": "Status updated"})
        else:
            return Response({"error": "User is not a shop"}, status=status.HTTP_400_BAD_REQUEST)

class ShopUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        shop_id = request.data.get('shop_id')
        shop = Shop.objects.filter(id=shop_id, user=request.user).first()
        if shop:
            serializer = ShopSerializer(shop, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Shop not found"}, status=status.HTTP_400_BAD_REQUEST)

class ShopOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        orders = Order.objects.filter(shop__user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class ContactView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)