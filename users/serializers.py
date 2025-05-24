# serializers.py

from rest_framework import serializers
from .models import FavouriteBook

class FavouriteBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteBook
        fields = ['id', 'book_key', 'title', 'author', 'cover_i']