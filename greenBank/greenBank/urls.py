from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.urls import path, include, re_path
from django.contrib import admin
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Swagger UI",
        default_version="v1",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("api/auth/", include("authentication.urls")),
    path("api/transaction/", include("transaction.urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/cards/", include("cards.urls")),
    path("api/currencys/", include("currency.urls")),
    path("api/users/", include("users.urls")),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
