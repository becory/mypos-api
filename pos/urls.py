"""pos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import include, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from Auth.views import POSTokenVerifyView
from patches import routers
from django.conf.urls.static import static
from django.conf import settings
import debug_toolbar

from Customer.urls import router as Customer_api
from Stock.urls import router as Stock_api
from Menu.urls import router as Menu_api
from Order.urls import router as Order_api
from Analysis.urls import router as Analysis_api
from Auth.urls import router as Auth_api

router = routers.DefaultRouter()
router.extend(Customer_api)
router.extend(Stock_api)
router.extend(Menu_api)
router.extend(Order_api)
router.extend(Analysis_api)
router.extend(Auth_api)

schema_view = get_schema_view(
    openapi.Info(
        title="POS API",
        default_version='v1',
        description="pos demo project",
        #    terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(name="Huang Ssu Yuan", email="ssuyuanhuang@gmail.com"),
        # license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,), )

urlpatterns = [
                  path('__debug__/', include(debug_toolbar.urls)),
                  path('api-auth/', include('rest_framework.urls')),
                  path('api/', include(router.urls)),
                  path('api/token/obtain/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
                  path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                  path('api/token/verify/', POSTokenVerifyView.as_view(), name='token_verify'),
                  path('admin/', admin.site.urls),
                  path('swagger/<str:format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
                  path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                  path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
