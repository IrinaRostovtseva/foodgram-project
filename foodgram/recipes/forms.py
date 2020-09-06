from django import forms

from .models import Recipe, Ingredient, Tag


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('name', 'cook_time',
                  'description', 'image',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form__input'}),
            'cook_time': forms.NumberInput(
                attrs={'class': 'form__input',
                       'id': 'id_time',
                       'name': 'time'}),
            'description': forms.Textarea(attrs={'class': 'form__textarea',
                                                 'rows': '8'}),
            'image': forms.FileInput(attrs={'id': 'id_file', 'name': 'file'})
        }
        labels = {
            'image': 'Загрузить фото'
        }
