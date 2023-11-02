from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('shop_app.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
]
