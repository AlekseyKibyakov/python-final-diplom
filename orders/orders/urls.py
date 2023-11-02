from baton.autodiscover import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', 
         SpectacularAPIView.as_view(), 
         name='schema'),
    path('api/schema/swagger-ui/', 
         SpectacularSwaggerView.as_view(url_name='schema'), 
         name='swagger-ui'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('shop_app.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('baton/', include('baton.urls'))
]
