from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("recipes/", views.home, name="recipes"),
    path("add/", views.add_recipe, name="add_recipe"),
    path("edit/<int:recipe_id>/", views.edit_recipe, name="edit_recipe"),
    path("delete/<int:recipe_id>/", views.delete_recipe, name="delete_recipe"),
    path("save-api-recipe/", views.save_api_recipe, name="save_api_recipe"),
    path("breakfast/", views.breakfast, name="breakfast"),
    path("lunch/", views.lunch, name="lunch"),
    path("dinner/", views.dinner, name="dinner"),
]