
document.addEventListener('DOMContentLoaded', function() {
    const scrollDownBtn = document.getElementById('scrollDownBtn');

    if (scrollDownBtn) {
        scrollDownBtn.addEventListener('click', function() {

            window.scrollTo({
                top: document.documentElement.scrollHeight,
                behavior: 'smooth'
            });
        });
    }
});


async function loadInBatches(items, batchSize, callback) {
  const results = [];
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await Promise.all(batch.map(callback));
    results.push(...batchResults);
  }
  return results;
}


// function for Open Router or Hugging Face
//
function bookLoader() {
  return {
    loading: false,
    loaded: false,
    books: [],

      async loadBooks(term) {
      this.loading = true;
      this.books = [];

      try {
        const response = await fetch('/api/books/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({ term }),
        });

        if (!response.ok) throw new Error('Network error: ' + response.status);

        const data = await response.json();
        if (!data.books || !Array.isArray(data.books)) throw new Error('Invalid data type');

        const results = await loadInBatches(data.books, 5, book =>
          fetch(`https://openlibrary.org/search.json?title=${encodeURIComponent(book)}&limit=1`)
            .then(res => res.json())
            .then(result => result.docs?.[0])
            .catch(err => {
              console.error(`Error loading book "${book}":`, err);
              return null;
            })
        );

        this.books = results.filter(book => book !== null);
        this.loaded = true;

      } catch (error) {
        console.error('Error loading books:', error);
        this.loaded = false;
      } finally {
        this.loading = false;
      }
    }
  };
}


function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function selector() {
  return {
    selectedTerm: 'long_term',
    tracks: [],

    setTerm(term) {
      this.selectedTerm = term;
      this.fetchTracks();
    },

    buttonClass(term) {
      return this.selectedTerm === term
        ? 'bg-[#3D7068] text-white shadow'
        : 'text-gray-200 hover:bg-[#3D7068]';
    },

    async fetchTracks() {
      try {
        const response = await fetch('/api/top/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({ term: this.selectedTerm }),
        });

        if (!response.ok) throw new Error('Ошибка сети: ' + response.status);

        const data = await response.json();

        if (data.error) {
          console.error('API Error:', data.error);
          this.tracks = [];
        } else {
          this.tracks = data;
        }
      } catch (e) {
        console.error('Fetch failed:', e);
      }
    }
  };
}
document.addEventListener('alpine:init', () => {
    Alpine.store('music', selector());
  });

document.addEventListener('alpine:init', () => {
  Alpine.store('favourites', {
    favourites: JSON.parse(document.getElementById('user-favourite-books')?.textContent || '[]'),

    isFavourite(book) {
      return this.favourites.some(f => f.book_key === book.key);
    },

    async addToFavourites(book) {
      try {
        const response = await fetch('/api/favourites/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify({
            book_key: book.key,
            title: book.title,
            author: book.author_name?.[0] || '',
            cover_i: book.cover_i || ''
          })
        });

        if (response.ok) {
          const data = await response.json();
          this.favourites.push(data);
        } else {
          console.error('Failed to add favourite:', await response.text());
        }
      } catch (e) {
        console.error('Error adding into favourites:', e);
      }
    },

    async removeFromFavourites(book) {
      const fav = this.favourites.find(f => f.book_key === book.key);
      if (!fav) return;

      try {
        const response = await fetch(`/api/favourites/${fav.id}/`, {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': getCookie('csrftoken')
          }
        });

        if (response.ok) {
          this.favourites = this.favourites.filter(f => f.book_key !== book.key);
        } else {
          console.error('Failed to remove favourite:', await response.text());
        }
      } catch (e) {
        console.error('Error deleting from favourites:', e);
      }
    },
    async removeFromProfileFavourites(book) {
          const fav = this.favourites.find(f => f.book_key === book.book_key);
          if (!fav) return;

          try {
            const response = await fetch(`/api/favourites/${fav.id}/`, {
              method: 'DELETE',
              headers: {
                'X-CSRFToken': getCookie('csrftoken')
              }
            });

            if (response.ok) {
              this.favourites = this.favourites.filter(f => f.book_key !== book.book_key);
            } else {
              console.error('Failed to remove favourite:', await response.text());
            }
          } catch (e) {
            console.error('Error deleting from favourites:', e);
          }
        },


    async toggleFavourite(book) {
      if (this.isFavourite(book)) {
        await this.removeFromFavourites(book);
      } else {
        await this.addToFavourites(book);
      }
    }
  });
});
