from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    CategoriesViewSet, TitleViewSet, GenresViewSet, UserSignupView,
    TokenView, ReviewsViewSet, CommentViewSet, UserViewSet, UserMeView,
)

router_v1 = SimpleRouter()
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'categories', CategoriesViewSet, basename='categories')
router_v1.register(r'genres', GenresViewSet, basename='genres')
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(
    r'titles/(?P<title_id>[^/.]+)/reviews',
    ReviewsViewSet,
    basename='reviews'
)
router_v1.register(
    'titles/(?P<title_id>[^/.]+)/reviews/(?P<review_id>[^/.]+)/comments',
    CommentViewSet,
    basename='comments'
)
auth_url = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('token/', TokenView.as_view(), name='token'),
]


urlpatterns = [
    path('v1/auth/', include(auth_url)),
    path('v1/users/me/', UserMeView.as_view(), name='me'),
    path('v1/', include(router_v1.urls)),
]
