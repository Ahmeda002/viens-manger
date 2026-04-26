import requests
from itertools import chain
from operator import attrgetter
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Recipe, Comment, MealComment
from .forms import RecipeForm


def home(request):
    if request.user.is_authenticated:
        recipes = Recipe.objects.filter(user=request.user).order_by('-created_at')
    else:
        recipes = []
    return render(request, 'recipes/home.html', {'recipes': recipes})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user
            recipe.save()
            return redirect('recipes')
    else:
        form = RecipeForm()
    return render(request, 'recipes/add_recipe.html', {'form': form})


@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, user=request.user)
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipes')
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recipes/edit_recipe.html', {'form': form, 'recipe': recipe})


@login_required
def delete_recipe(request, recipe_id):
    if request.method == 'POST':
        recipe = get_object_or_404(Recipe, id=recipe_id, user=request.user)
        next_url = request.POST.get('next', '')
        if recipe.image:
            recipe.image.delete(save=False)
        recipe.delete()
        if next_url:
            return redirect(next_url)
    return redirect('recipes')


@login_required
def save_api_recipe(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image_url = request.POST.get('image_url')
        ingredients = request.POST.get('ingredients', '')
        instructions = request.POST.get('instructions', '')

        meal_id = request.POST.get('meal_id', '')

        if title and description:
            Recipe.objects.create(
                user=request.user,
                title=title,
                description=description,
                image_url=image_url,
                ingredients=ingredients,
                instructions=instructions,
                meal_id=meal_id,
            )

    return redirect('recipes')


def meal_detail(request, meal_id):
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
    response = requests.get(url)
    data = response.json().get('meals') or []
    if not data:
        return redirect('home')
    meal = data[0]

    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('comment', '').strip()
        if text:
            MealComment.objects.create(meal_id=meal_id, user=request.user, text=text)
        return redirect('meal_detail', meal_id=meal_id)

    ingredients = []
    for i in range(1, 21):
        ingredient = (meal.get(f'strIngredient{i}') or '').strip()
        measure = (meal.get(f'strMeasure{i}') or '').strip()
        if ingredient:
            ingredients.append(f"{measure} {ingredient}".strip())

    comments = MealComment.objects.filter(meal_id=meal_id)

    saved_recipe = None
    if request.user.is_authenticated:
        saved_recipe = Recipe.objects.filter(user=request.user, meal_id=meal_id).first()

    return render(request, 'recipes/meal_detail.html', {
        'meal': meal,
        'ingredients': ingredients,
        'ingredients_text': '\n'.join(ingredients),
        'comments': comments,
        'saved_recipe': saved_recipe,
    })


def _fetch_meals(category):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}"
    response = requests.get(url)
    return response.json().get('meals', [])


def breakfast(request):
    return render(request, 'recipes/breakfast.html', {'meals': _fetch_meals('Breakfast')})


def lunch(request):
    return render(request, 'recipes/lunch.html', {'meals': _fetch_meals('Chicken')})


def dinner(request):
    return render(request, 'recipes/dinner.html', {'meals': _fetch_meals('Beef')})


def allow_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next=/comment/{recipe_id}/")
        text = request.POST.get('comment', '').strip()
        if text:
            Comment.objects.create(recipe=recipe, user=request.user, text=text)
        return redirect('allow_comment', recipe_id=recipe_id)

    recipe_comments = list(recipe.comments.all())
    meal_comments = list(MealComment.objects.filter(meal_id=recipe.meal_id)) if recipe.meal_id else []
    comments = sorted(chain(recipe_comments, meal_comments), key=attrgetter('created_at'), reverse=True)

    return render(request, 'recipes/allow_comment.html', {'recipe': recipe, 'comments': comments})
