from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from backend.admin import custom_admin_site
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", custom_admin_site.urls),
    path("api/", include([
        path("product/", include("product.urls")),
    ])),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name= 'schema'), name='swagger-ui'),
    path('silk/', include('silk.urls', namespace='silk')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
