# Viens Manger 🍽️

A full-stack recipe management web app built with Django. Users can create and manage their own recipes, browse meals fetched live from an external API, and save favorites to their personal collection.

## Features

- **User Authentication** — Register, login, and logout with secure session management
- **Recipe CRUD** — Create, edit, and delete your own recipes with image uploads; ownership-based access control prevents other users from modifying your recipes
- **External API Integration** — Breakfast, lunch, and dinner pages pull live meal data from [TheMealDB API](https://www.themealdb.com), with the ability to save any API meal to your personal collection
- **Search** — Search across both your saved recipes and live API results simultaneously
- **Today's Special** — Automatically suggests a meal based on the time of day
- **Comments** — Leave comments with text and images on any recipe
- **User Profiles** — Upload a profile avatar and update your email

## Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, Bootstrap 5
- **Database:** SQLite
- **External API:** TheMealDB REST API
- **Testing:** Django TestCase (25+ unit and integration tests)

## Getting Started

```bash
# Clone the repository
git clone https://github.com/Ahmeda002/viens-manger.git
cd viens-manger

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run the development server
python manage.py runserver
```

Then open your browser and go to `http://127.0.0.1:8000`

## Running Tests

```bash
python manage.py test
```

The test suite covers authentication flows, CRUD operations, ownership access control, API recipe saving, and comment functionality.

## Project Structure

```
viens-manger/
├── config/          # Django project settings and root URLs
├── recipes/         # Main app — models, views, forms, URLs, tests
│   └── templates/   # HTML templates using Bootstrap 5
├── media/           # User-uploaded images (recipe images, avatars)
└── manage.py
```

## API Reference

Meal data is provided by [TheMealDB](https://www.themealdb.com) — a free, open meal database with thousands of recipes across multiple categories.
