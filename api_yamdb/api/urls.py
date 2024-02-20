from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import CategoryViewSet, TitleViewSet

router_v1 = SimpleRouter()
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'categories', CategoryViewSet, basename='categories')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
