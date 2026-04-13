# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Viens Manger is a Django recipe management web app. Users can add/edit/delete their own recipes and browse meals fetched from the TheMealDB external API.

## Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Run tests
python manage.py test

# Run a single test
python manage.py test recipes.tests.TestClassName.test_method_name

# Create admin superuser
python manage.py createsuperuser
```

## Architecture

**Project layout:**
- `config/` — Django project settings, root `urls.py`, wsgi/asgi
- `recipes/` — The single Django app containing all functionality

**Data model:** A single `Recipe` model with `title`, `description`, `image` (uploaded file), `image_url` (for API-sourced images), and timestamps.

**Two sources of recipe data:**
1. User-created recipes (stored in SQLite, served from `home` view)
2. TheMealDB API recipes (fetched live in `breakfast`, `lunch`, `dinner` views — Breakfast, Chicken, Beef categories respectively). API recipes can be saved locally via `save_api_recipe`.

**URL structure:**
- `/` and `/recipes/` → home (all saved recipes)
- `/add/`, `/edit/<id>/`, `/delete/<id>/` → CRUD for user recipes
- `/breakfast/`, `/lunch/`, `/dinner/` → live API meal pages
- `/save-api-recipe/` → save an API meal to the local DB
- `/allow-comment/` → comment feature (not yet fully implemented)

**Templates** use Bootstrap 5.3.0 (CDN). `recipes/templates/base.html` is the base layout with navbar; all other templates extend it. Recipe-specific templates live in `recipes/templates/recipes/`.

**Media files** (user-uploaded images) are stored in `media/recipe_images/` and served at `/media/` in development.

## Key Notes

- The `allow_comment` view currently only prints to the console — it is not yet implemented.
- Both uploaded images (`image` field) and remote image URLs (`image_url` field) are supported on Recipe; templates should check which is present.
- Django version is 6.0.2; `Pillow` is required for `ImageField` support.
