from django.shortcuts import render
from .models import Recipe

def home(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/home.html', {'recipes': recipes})

def recipies(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/recipies.html', {'recipes': recipes})