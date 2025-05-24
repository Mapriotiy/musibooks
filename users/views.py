from django.contrib.auth.decorators import login_required
from django.contrib.auth  import logout
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from social_django.models import  UserSocialAuth
from django.shortcuts import render, redirect
from rest_framework import viewsets, permissions
from .models import FavouriteBook
from .serializers import FavouriteBookSerializer
from .util import get_spotify_profile_data, get_user_private_data
from .ai_util import prompt_ai, extract_json_from_text
import json


# Create your views here.
def index(request):
    spotify_data = None
    private_data = None
    user_favourites = []

    if request.user.is_authenticated:
        spotify_data = get_spotify_profile_data(request.user)
        user_favourites = list(
        FavouriteBook.objects.filter(user=request.user).values('id', 'book_key', 'title', 'author', 'cover_i'))

    return render(request, 'index.html', {'spotify_data': spotify_data, 'user_favourite_books': json.dumps(user_favourites, cls=DjangoJSONEncoder)})


def logout_view(request):
    logout(request)
    return redirect('/')

def profile(request):
    spotify_data = get_spotify_profile_data(request.user)
    user_favourites=list(
            FavouriteBook.objects.filter(user=request.user).values('id', 'book_key', 'title', 'author', 'cover_i'))

    return render(request, 'profile.html', {
        'spotify_data': spotify_data,
        'user_favourite_books': json.dumps(user_favourites, cls=DjangoJSONEncoder),
    })

def update_top_api(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)

            term = data.get('term', 'all_time')
            private_data = get_user_private_data(request.user, term)

            return JsonResponse(private_data, safe=False)

        except Exception as e:
            print(f'Error: {e}')
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Unauthorized or bad method'}, status=403)

#Use with Open Router or Hugging Face
#
def books_api(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            term = data.get('term', 'all_time')
            tracks = ''
            books = []
            private_data = get_user_private_data(request.user, term, 25)
            for track in private_data:
                tracks += f" {track['name']} - {track['artists'][0]}; "

            books_str = prompt_ai(
                "Recommend me STRICTLY 5 POPULAR BOOK NAMES(NO AUTHOR NAMES IN OUTPUT) in JSON format(Example:\n"
                '{"books": ["Book 1", "Book 2"]})'
                f" Based on that user likes these tracks {tracks} BUT ALSO YOU SHOULD ADD SOME NEW GENRES FOR THINGS TO BE INTERESTING "
                "NO EXTRA WORDS ALSO WRITE 1984 AS Nineteen eighty-four"
            )
            books = extract_json_from_text(books_str)

            # debug mode
            # txt = ['Nineteen eighty-four', 'Brave New World', 'The Catcher in the Rye', 'The Bell Jar',
            #          'Fahrenheit 451']
            #
            # data = {'books': txt}
            #
            # books = data
            # print(books)
            return JsonResponse(books, safe=False)

        except Exception as e:
            print(f'Error: {e}')
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Unauthorized or bad method'}, status=403)

class FavouriteBookViewSet(viewsets.ModelViewSet):
    serializer_class = FavouriteBookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavouriteBook.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)