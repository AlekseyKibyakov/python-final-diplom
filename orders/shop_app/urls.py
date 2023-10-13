from django.urls import path
from .views import RegisterBuyerView, ConfirmEmailView, LoginView, UserProfileView, ProductSearchView, ShopOrdersView, ContactView, UserOrdersView, CartView, UpdatePriceView, ShopStatusView, ShopUpdateView

urlpatterns = [
    path('register/', RegisterBuyerView.as_view(), name='register'),
    path('confirm-email/', ConfirmEmailView.as_view(), name='confirm-email'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('search/', ProductSearchView.as_view(), name='search'),
    path('shop-orders/', ShopOrdersView.as_view(), name='shop-orders'),
    path('contacts/', ContactView.as_view(), name='contacts'),
    path('user-orders/', UserOrdersView.as_view(), name='user-orders'),
    path('cart/', CartView.as_view(), name='cart'),
    path('update-price/', UpdatePriceView.as_view(), name='update-price'),
    path('shop-status/', ShopStatusView.as_view(), name='shop-status'),
    path('shop-update/', ShopUpdateView.as_view(), name='shop-update'),
]