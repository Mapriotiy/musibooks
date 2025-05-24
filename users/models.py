from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class FavouriteBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_key = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True, null=True)
    cover_i = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'book_key')
