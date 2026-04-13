import requests
from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipe
from .forms import RecipeForm


def home(request):
    recipes = Recipe.objects.all().order_by('-created_at')
    return render(request, 'recipes/home.html', {'recipes': recipes})


def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('recipes')
    else:
        form = RecipeForm()

    return render(request, 'recipes/add_recipe.html', {'form': form})


def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipes')
    else:
        form = RecipeForm(instance=recipe)

    return render(request, 'recipes/edit_recipe.html', {'form': form, 'recipe': recipe})


def delete_recipe(request, recipe_id):
    if request.method == 'POST':
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if recipe.image:
            recipe.image.delete(save=False)
        recipe.delete()
    return redirect('recipes')


def save_api_recipe(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image_url = request.POST.get('image_url')

        if title and description:
            Recipe.objects.create(
                title=title,
                description=description,
                image_url=image_url
            )

    return redirect('recipes')


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

def allow_comment(request):
    if request.method == 'POST':
        comment = request.POST.get('comment')
        # Here you would typically save the comment to the database
        # For this example, we'll just print it to the console
        print(f"Received comment: {comment}")
    return redirect('home')