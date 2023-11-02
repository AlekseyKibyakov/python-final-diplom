import os
from django.contrib.auth import get_user_model, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from orders.settings import EMAIL_HOST_PASSWORD, EMAIL_HOST_USER
from shop_app.permissions import IsShop
from .models import Product, Order, OrderItem, ProductInfo, Shop, Contact, ConfirmEmailToken
from .serializers import UserSerializer, ProductSerializer, OrderSerializer, \
    OrderItemSerializer, ProductInfoSerializer, ShopSerializer, ContactSerializer
User = get_user_model()
from django.core.mail import send_mail

from drf_spectacular.utils import extend_schema

class RegisterBuyerView(APIView):
    """
    Регистрация покупателя.
    """
    @extend_schema(
        request=UserSerializer,
        responses={status.HTTP_201_CREATED: UserSerializer},
        description="Регистрация покупателя"
    )
    def post(self, request, format=None):
        """
        Создает нового пользователя с ролью "buyer".
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user_type = serializer.validated_data.get('type', 'buyer')
            user = User.objects.create_user(
                email=serializer.validated_data['email'],
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
                type=user_type
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
    """
    Подтверждение email.
    """
    @extend_schema(
        request={"key": "string"},
        responses={status.HTTP_200_OK: {"message": "string"}, status.HTTP_400_BAD_REQUEST: {"error": "string"}},
        description="Подтверждение email"
    )
    def post(self, request, format=None):
        """
        Подтверждает email пользователя с помощью ключа подтверждения.
        """
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
    """
    Вход в систему.
    """
    @extend_schema(
        request={"email": "string", "password": "string"},
        responses={status.HTTP_200_OK: {"token": "string"}, status.HTTP_400_BAD_REQUEST: {"error": "string"}},
        description="Вход в систему"
    )
    def post(self, request, format=None):
        """
        Проверяет учетные данные пользователя и возвращает токен доступа.
        """
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    """
    Профиль пользователя.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={status.HTTP_200_OK: UserSerializer},
        description="Получение профиля пользователя"
    )
    def get(self, request, format=None):
        """
        Возвращает профиль текущего пользователя.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        request=UserSerializer,
        responses={status.HTTP_200_OK: UserSerializer, status.HTTP_400_BAD_REQUEST: {"error": "string"}},
        description="Обновление профиля пользователя"
    )
    def put(self, request, format=None):
        """
        Обновляет профиль текущего пользователя.
        """
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductSearchView(APIView):
    """
    Поиск продуктов.
    """
    @extend_schema(
        responses={status.HTTP_200_OK: ProductSerializer(many=True)},
        description="Поиск продуктов"
    )
    def get(self, request, format=None):
        """
        Выполняет поиск продуктов по заданному запросу.
        """
        query = request.query_params.get('query', '')
        products = Product.objects.filter(name__icontains=query)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class CartView(APIView):
    """
    Корзина пользователя.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={status.HTTP_200_OK: OrderSerializer},
        description="Получение корзины пользователя"
    )
    def get(self, request, format=None):
        """
        Возвращает корзину пользователя.
        """
        order = Order.objects.filter(user=request.user, state='cart').first()
        if order:
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        else:
            return Response({"message": "Cart is empty"})

    @extend_schema(
        request={"product_id": "integer", "quantity": "integer"},
        responses={status.HTTP_200_OK: {"message": "string"}, status.HTTP_400_BAD_REQUEST: {"error": "string"}},
        description="Добавление продукта в корзину"
    )
    def post(self, request, format=None):
        """
        Добавляет продукт в корзину пользователя.
        """
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

    @extend_schema(
        request={"product_id": "integer"},
        responses={status.HTTP_200_OK: {"message": "string"}, status.HTTP_400_BAD_REQUEST: {"error": "string"}},
        description="Удаление продукта из корзины"
    )
    def delete(self, request, format=None):
        """
        Удаляет продукт из корзины пользователя.
        """
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

class CreateShopView(APIView):
    permission_classes = [IsAuthenticated, IsShop]

    @extend_schema(
        request=ShopSerializer,
        responses={status.HTTP_201_CREATED: ShopSerializer},
        description="Создание магазина"
    )
    def post(self, request, format=None):
        """
        Создает новый магазин для авторизованного пользователя типа "shop".
        """
        user = request.user
        if user.type != 'shop':
            return Response({"error": "User is not a shop"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ShopSerializer(data=request.data)
        if serializer.is_valid():
            shop = serializer.save(user=user)
            return Response(ShopSerializer(shop).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdatePriceView(APIView):
    permission_classes = [IsAuthenticated, IsShop]

    @extend_schema(
        request={
            "shop_id": "integer",
            "product_infos": [{
                "id": "integer",
                "quantity": "integer",
                "other_field": "string"  # Дополнительные поля сериализатора
            }]
        },
        responses={status.HTTP_200_OK: {"message": "string"}, status.HTTP_400_BAD_REQUEST: {"error": "string"}},
        description="Обновление цен на товары"
    )
    def put(self, request, format=None):
        """
        Обновляет информацию о ценах на товары для определенного магазина.
        """
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
    permission_classes = [IsAuthenticated, IsShop]

    @extend_schema(
        request={"is_active": "boolean"},
        responses={status.HTTP_200_OK: {"message": "string"}},
        description="Обновление статуса магазина"
    )
    def put(self, request, format=None):
        """
        Обновляет статус магазина пользователя.
        """
        user = request.user
        user.is_active = request.data.get('is_active')
        user.save()
        return Response({"message": "Status updated"})
        

class ShopUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsShop]

    @extend_schema(
        request={"shop_id": "integer"},
        responses={status.HTTP_200_OK: ShopSerializer, status.HTTP_400_BAD_REQUEST: {"error": "string"}},
        description="Обновление информации о магазине"
    )
    def put(self, request, format=None):
        """
        Обновляет информацию о магазине.
        """
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
    permission_classes = [IsAuthenticated, IsShop]

    @extend_schema(
        responses={status.HTTP_200_OK: OrderSerializer(many=True)},
        description="Получение заказов магазина"
    )
    def get(self, request, format=None):
        """
        Получает список заказов для магазина текущего пользователя.
        """
        orders = Order.objects.filter(shop__user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class ContactView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={status.HTTP_200_OK: ContactSerializer(many=True)},
        description="Получение контактов пользователя"
    )
    def get(self, request, format=None):
        """
        Получает список контактов текущего пользователя.
        """
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=ContactSerializer,
        responses={status.HTTP_201_CREATED: ContactSerializer, status.HTTP_400_BAD_REQUEST: {"error": "string"}},
        description="Создание контакта пользователя"
    )
    def post(self, request, format=None):
        """
        Создает новый контакт для пользователя.
        """
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={status.HTTP_200_OK: OrderSerializer(many=True)},
        description="Получение заказов пользователя"
    )
    def get(self, request, format=None):
        """
        Получает список заказов пользователя.
        """
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=OrderSerializer,
        responses={status.HTTP_200_OK: OrderSerializer, status.HTTP_400_BAD_REQUEST: {"error": "string"}},
        description="Создание заказа пользователя"
    )
    def post(self, request, format=None):
        """
        Создает новый заказ для пользователя.
        """
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)