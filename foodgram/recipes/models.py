from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Product(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название продукта')
    unit = models.CharField(max_length=10, verbose_name='Единицы измерения')

    def __str__(self):
        return f'{self.title}, {self.unit}'


class Tag(models.Model):
    name = models.CharField(max_length=10, verbose_name='Название тега')
    slug = models.SlugField(verbose_name='Слаг тега')

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор рецепта',
                               related_name='recipe_author')
    name = models.CharField(max_length=100, verbose_name='Название рецепта')
    description = models.TextField(verbose_name='Описание рецепта')
    image = models.ImageField(upload_to='recipes/',
                              verbose_name='Изображение блюда')
    tags = models.ManyToManyField(Tag, verbose_name='Теги', blank=True)
    ingredients = models.ManyToManyField(
        Product, through='Ingredient', related_name='recipe_ingredients')
    cook_time = models.IntegerField(verbose_name='Время приготовления')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Время публикации', db_index=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.FloatField(verbose_name='Количество ингредиента')

    class Meta:
        unique_together = ('ingredient', 'amount', 'recipe')

    def __str__(self):
        return f'{self.amount}'


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe)
