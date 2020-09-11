# Generated by Django 3.1 on 2020-09-09 13:57
import csv
import os

from django.conf import settings
from django.db import migrations


def write_ingredients(apps, schema_editor):
    ingredients = os.path.join(settings.BASE_DIR, 'ingredients.csv')
    with open(ingredients, 'r') as ing:
        f = csv.reader(ing, delimiter=',')
        Ingredient = apps.get_model('recipes.Product')
        for row in f:
            product = Ingredient(title=row[0], unit=row[1])
            product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(write_ingredients)
    ]