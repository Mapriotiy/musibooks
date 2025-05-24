import requests
from social_django.utils import load_strategy
import time

def refresh_spotify_token(user):
    social = user.social_auth.get(provider='spotify')
    strategy = load_strategy()
    social.refresh_token(strategy)
    social.save()
    return social.extra_data['access_token']

def get_valid_spotify_token(user):
    social = user.social_auth.get(provider='spotify')
    expires_at = social.extra_data.get('expires_at', 0)
    now = int(time.time())

    if expires_at - now < 60:
        strategy = load_strategy()
        social.refresh_token(strategy)
        social.save()

    return social.extra_data['access_token']

def get_spotify_profile_data(user):
    try:
        access_token = get_valid_spotify_token(user)

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                'display_name': data.get('display_name'),
                'image_url': data.get('images', [{}])[0].get('url'),
            }
        else:
            print(f'Error: {response.status_code} — {response.text}')
    except Exception as e:
        print(f'Error: {e}')
    return None

def get_user_private_data(user, term = 'long_term', limit = 5):
    try:
        access_token = get_valid_spotify_token(user)

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get(f'https://api.spotify.com/v1/me/top/tracks?limit={limit}&time_range={term}', headers=headers)
        if response.status_code == 200:
            data = response.json()
            tracks = []

            for item in data.get('items', []):
                images = item.get('album', {}).get('images', [])
                genres = item.get('album', {}).get('genres', [])
                image_url = images[0]['url'] if images else None
                tracks.append({
                            'id': item.get('id'),
                            'name': item.get('name'),
                            'type': item.get('type'),
                            'popularity': item.get('popularity'),
                            'url': item.get('external_urls', {}).get('spotify'),
                            'artists': [artist['name'] for artist in item.get('artists', [])],
                            'images':image_url,
                        })

            return tracks
        else:
            print(f'Error: {response.status_code} — {response.text}')
    except Exception as e:
        print(f'Error: {e}')
    return None
