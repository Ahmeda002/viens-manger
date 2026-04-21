from django import forms
from .models import Recipe
from .models import Comment 


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'instructions', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment 
        fields = ['text','image']



