# Generated by Django 3.1 on 2020-09-07 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20200906_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, to='recipes.Tag', verbose_name='Теги'),
        ),
    ]
