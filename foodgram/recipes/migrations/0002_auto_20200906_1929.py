# Generated by Django 3.1 on 2020-09-06 19:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ingredient',
            unique_together={('ingredient', 'amount', 'recipe')},
        ),
    ]
