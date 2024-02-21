from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    CategoriesViewSet,
    TitleViewSet,
    GenresViewSet,
    ReviewsViewSet,
    CommentViewSet
)

router_v1 = SimpleRouter()
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'categories', CategoriesViewSet, basename='categories')
router_v1.register(r'genres', GenresViewSet, basename='genres')
router_v1.register(
    r'titles/(?P<title_id>[^/.]+)/reviews/',
    ReviewsViewSet,
    basename='reviews'
)
router_v1.register(
    'titles/(?P<title_id>[^/.]+)/reviews/(?P<review_id>[^/.]+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
