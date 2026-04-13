from django.contrib import admin
from .models import Recipe, Comment, MealComment


admin.site.register(Recipe)
admin.site.register(Comment)
admin.site.register(MealComment)