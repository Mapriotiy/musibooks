import profile

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = 'users'

router = DefaultRouter()
router.register(r'favourites', FavouriteBookViewSet, basename='favourites')

urlpatterns = [
    path('', index, name=''),
    path('profile/', profile, name='profile'),
    path('logout/', logout_view, name='logout'),
    path('api/top/', update_top_api, name='top_api'),
    path('api/books/', books_api, name='books_api'), #Only for Open Router or Hugging Face
    path('api/', include(router.urls)),
]