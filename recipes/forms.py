from django import forms

from .models import Recipe, Tag


class RecipeForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'tags__checkbox'}),
        to_field_name='slug',
        required=False
    )

    class Meta:
        model = Recipe
        fields = ('name', 'cook_time', 'tags',
                  'description', 'image',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form__input'}),
            'cook_time': forms.NumberInput(
                attrs={'class': 'form__input',
                       'id': 'id_time',
                       'name': 'time'}),
            'description': forms.Textarea(attrs={'class': 'form__textarea',
                                                 'rows': '8'}),
        }
        labels = {
            'image': 'Загрузить фото'
        }
