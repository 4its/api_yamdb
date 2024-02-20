from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    CategoryViewSet,
    TitleViewSet,
    GenresViewSet,
    ReviewsViewSet,
    CommentViewSet
)

router_v1 = SimpleRouter()
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenresViewSet, basename='genres')
router_v1.register(r'reviews', ReviewsViewSet, basename='reviews')
router_v1.register(r'comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
