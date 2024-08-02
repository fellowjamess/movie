import requests
from bs4 import BeautifulSoup
import json
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from collections import Counter
import os
import time
import re

def get_favorite_movies(username):
    url = f"https://letterboxd.com/{username}/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        favorites_section = soup.find('section', id='favourites')
        if not favorites_section:
            print("Favorites section not found. Check if the username is correct.")
            return []

        movies = []
        for poster in favorites_section.select('.poster-container'):
            movie_div = poster.find('div', class_='film-poster')
            if movie_div:
                movie_id = movie_div['data-film-id']
                movieId_url = "/".join(movie_id)
                title = movie_div.find('img')['alt']
                film_slug = movie_div['data-film-slug']
                poster_url = f"https://a.ltrbxd.com/resized/film-poster/{movieId_url}/{movie_id}-{film_slug}-0-2000-0-3000-crop.jpg"
                movies.append({'id': movie_id, 'title': title, 'film_slug': film_slug, 'poster_url': poster_url})
        
        return movies
    except requests.RequestException as e:
        print(f"Error fetching user page: {str(e)}")
        return []

def remove_numbers_from_slug(slug):
    return re.sub(r'-\d+$', '', re.sub(r'-\d+', '', slug))

def get_dominant_color(image_url, film_slug, movie_id):
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            img = img.convert('RGB')
            pixels = list(img.getdata())
            color_counts = Counter(pixels)
            dominant_color = color_counts.most_common(1)[0][0]
            return dominant_color
        except (requests.RequestException, UnidentifiedImageError) as e:
            print(f"Error processing image (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(10)
            elif attempt == max_retries - 1:
                film_slug_no_numbers = remove_numbers_from_slug(film_slug)
                new_image_url = f"https://a.ltrbxd.com/resized/film-poster/{'/'.join(movie_id)}/{movie_id}-{film_slug_no_numbers}-0-2000-0-3000-crop.jpg"
                for retry in range(max_retries):
                    try:
                        response = requests.get(new_image_url, timeout=10)
                        response.raise_for_status()
                        img = Image.open(BytesIO(response.content))
                        img = img.convert('RGB')
                        pixels = list(img.getdata())
                        color_counts = Counter(pixels)
                        dominant_color = color_counts.most_common(1)[0][0]
                        return dominant_color
                    except (requests.RequestException, UnidentifiedImageError) as e:
                        print(f"Error processing image with modified slug (attempt {retry + 1}/{max_retries}): {str(e)}")
                        if retry < max_retries - 1:
                            time.sleep(2)
    print(f"Failed to process image after {max_retries * 2} attempts")
    return None

def process_movies(username):
    json_file = 'letterboxd_favorites.json'
    
    # Load existing data or create empty list
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = []
    
    # Get favorite movies
    favorite_movies = get_favorite_movies(username)
    
    if not favorite_movies:
        print("No favorite movies found. Check the username and try again.")
        return
    
    # Process each movie
    for movie in favorite_movies:
        # Check if movie already exists in JSON
        if not any(item['id'] == movie['id'] for item in existing_data):
            rgb = get_dominant_color(movie['poster_url'], movie['film_slug'], movie['id'])
            if rgb:
                movie_data = {
                    "id": movie['id'],
                    "title": movie['title'],
                    "rgb": rgb
                }
                existing_data.append(movie_data)
                print(f"Processed: {movie['title']}")
            else:
                print(f"Skipped: {movie['title']} (failed to get color)")
        else:
            print(f"Skipped: {movie['title']} (already exists)")
    
    # Save updated data to JSON file
    if existing_data:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {json_file}")
    else:
        print("No data to save. JSON file was not created.")

# Usage
username = "karlimmer"
process_movies(username)
