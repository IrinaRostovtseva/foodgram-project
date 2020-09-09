import json
from urllib.parse import unquote

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from users.models import Subscription

from .create_file import write_into_file
from .forms import RecipeForm
from .models import Favorite, Ingredient, Product, Purchase, Recipe, Tag, User


TAGS = Tag.objects.all()


def _get_filtered_recipes(request, objs):
    tags = request.GET.getlist('tag')
    if tags:
        return objs.prefetch_related('author', 'tags').filter(
            tags__slug__in=tags).distinct().order_by('-pub_date')
    else:
        return objs.prefetch_related('author', 'tags',).order_by('-pub_date')


def _get_counter(request):
    try:
        purchase = Purchase.objects.get(user=request.user)
        shop_count = purchase.recipes.count()
    except ObjectDoesNotExist:
        shop_count = 0
    return shop_count


def _get_purchases_list(request):
    try:
        purchase = Purchase.objects.get(user=request.user)
        purchase_list = purchase.recipes.all()
    except ObjectDoesNotExist:
        purchase_list = []
    return purchase_list


def index(request):
    recipe_list = _get_filtered_recipes(request, Recipe.objects)
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'all_tags': TAGS,
        'page': page,
        'paginator': paginator
    }
    user = request.user
    if user.is_authenticated:
        shop_count = _get_counter(request)
        purchase_list = _get_purchases_list(request)
        try:
            favorite = Favorite.objects.get(user=user)
            context['favorites'] = favorite.recipes.all()
        except ObjectDoesNotExist:
            context['favorites'] = []
        context['shop_count'] = shop_count
        context['purchase_list'] = purchase_list
    return render(request, 'index.html', context)


def profile(request, user_id):
    if request.method == 'GET':
        profile = get_object_or_404(User, id=user_id)
        recipes_list = _get_filtered_recipes(request, Recipe.objects)
        paginator = Paginator(recipes_list.filter(author=profile), 6)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        context = {
            'all_tags': TAGS,
            'profile': profile,
            'page': page,
            'paginator': paginator
        }
        # Если юзер авторизован, добавляет в контекст счетчик
        # покупок и избранное
        if request.user.is_authenticated:
            is_subscribed = Subscription.objects.filter(
                user=request.user, author=profile).exists()
            shop_count = _get_counter(request)
            purchase_list = _get_purchases_list(request)
            try:
                favorite = Favorite.objects.get(user=request.user)
                context['favorites'] = favorite.recipes.all()
            except ObjectDoesNotExist:
                context['favorites'] = []
            context['is_subscribed'] = is_subscribed
            context['shop_count'] = shop_count
            context['purchase_list'] = purchase_list
        return render(request, 'profile.html', context)


def recipe_detail(request, recipe_id):
    if request.method == 'GET':
        recipe = get_object_or_404(Recipe, id=recipe_id)
        author = recipe.author
        context = {
            'recipe': recipe,
        }
        user = request.user
        if user.is_authenticated:
            is_subscribed = Subscription.objects.filter(
                user=user, author=author).exists()
            shop_count = _get_counter(request)
            try:
                favorite = Favorite.objects.get(user=user)
                is_favorite = favorite.recipes.filter(id=recipe_id).exists()
            except ObjectDoesNotExist:
                is_favorite = False
            try:
                purchase = Purchase.objects.get(user=user)
                is_purchased = purchase.recipes.filter(id=recipe_id).exists()
            except ObjectDoesNotExist:
                is_purchased = False
            context['is_subscribed'] = is_subscribed
            context['is_favorite'] = is_favorite
            context['shop_count'] = shop_count
            context['is_purchased'] = is_purchased
        return render(request, 'recipe_detail.html', context)


@login_required(login_url='auth/login/')
def favorite(request):
    # GET-запрос на страницу с избранными рецептами
    if request.method == 'GET':
        auth_user = get_object_or_404(User, username=request.user.username)
        try:
            favorite = Favorite.objects.get(user=auth_user)
            recipes_list = _get_filtered_recipes(request, favorite.recipes)
        except ObjectDoesNotExist:
            recipes_list = []
        shop_count = _get_counter(request)
        purchase_list = _get_purchases_list(request)
        paginator = Paginator(recipes_list, 6)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        context = {
            'all_tag': TAGS,
            'favorites': page,
            'shop_count': shop_count,
            'purchase_list': purchase_list,
            'paginator': paginator,
            'page': page
        }
        return render(request, 'favorites.html', context)
    # POST-запрос на добавление в избранное
    elif request.method == 'POST':
        json_data = json.loads(request.body.decode())
        recipe_id = int(json_data['id'])
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, id=request.user.id)
        data = {'success': 'true'}
        try:
            favorite = Favorite.objects.get(user=user)
        except ObjectDoesNotExist:
            favorite = Favorite(user=user)
            favorite.save()
            favorite.recipes.add(recipe)
        is_favorite = favorite.recipes.filter(id=recipe_id).exists()
        if is_favorite:
            data['success'] = 'false'
        else:
            favorite.recipes.add(recipe)
        return JsonResponse(data)


@login_required(login_url='auth/login/')
def delete_favorite(request, recipe_id):
    if request.method == 'DELETE':
        user = get_object_or_404(User, username=request.user.username)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data = {'success': 'true'}
        try:
            favorite = Favorite.objects.get(user=user)
        except ObjectDoesNotExist:
            data['success'] = 'false'
        try:
            favorite.recipes.remove(recipe)
        except ObjectDoesNotExist:
            data['success'] = 'false'
        return JsonResponse(data)


@login_required(login_url='auth/login/')
def get_subscriptions(request):
    if request.method == 'GET':
        auth_user = get_object_or_404(User, username=request.user.username)
        try:
            subscriptions = Subscription.objects.filter(user=auth_user)
        except ObjectDoesNotExist:
            subscriptions = []
        shop_count = _get_counter(request)
        page_num = request.GET.get('page')
        paginator = Paginator(subscriptions, 6)
        page = paginator.get_page(page_num)
        context = {
            'shop_count': shop_count,
            'paginator': paginator,
            'page': page,
        }
        return render(request, 'subscriptions.html', context)


@login_required(login_url='auth/login/')
def subscription(request):
    if request.method == 'POST':
        json_data = json.loads(request.body.decode())
        auth_user = get_object_or_404(User, username=request.user.username)
        author_id = int(json_data['id'])
        author = get_object_or_404(User, id=author_id)
        is_exist = Subscription.objects.filter(
            user=auth_user, author=author).exists()
        data = {'success': 'true'}
        if is_exist:
            data['success'] = 'false'
        else:
            Subscription.objects.create(user=auth_user, author=author)
        return JsonResponse(data)


@login_required(login_url='auth/login/')
def delete_subscription(request, author_id):
    if request.method == 'DELETE':
        auth_user = get_object_or_404(User, id=request.user.id)
        author = get_object_or_404(User, id=author_id)
        data = {'success': 'true'}
        try:
            follow = Subscription.objects.filter(
                user=auth_user, author=author)
            follow.delete()
        except ObjectDoesNotExist:
            data['success'] = 'false'
        return JsonResponse(data)


@login_required(login_url='auth/login/')
def purchase(request):
    # GET-запрос на страницу со списком покупок
    if request.method == 'GET':
        user = get_object_or_404(User, id=request.user.id)
        try:
            purchase = Purchase.objects.get(user=user)
            recipes_list = purchase.recipes.all()
            shop_count = purchase.recipes.count()
        except ObjectDoesNotExist:
            recipes_list = []
            shop_count = 0
        context = {
            'recipes_list': recipes_list,
            'shop_count': shop_count,
        }
        return render(request, 'purchases.html', context)
    # POST-запрос на добавление рецепта в список покупок
    if request.method == 'POST':
        json_data = json.loads(request.body.decode())
        recipe_id = int(json_data['id'])
        user = get_object_or_404(User, id=request.user.id)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data = {
            'success': 'true'
        }
        try:
            purchase = Purchase.objects.get(user=user)
        except ObjectDoesNotExist:
            purchase = Purchase(user=user)
            purchase.save()
        if purchase.recipes.filter(id=recipe_id).exists():
            data['success'] = 'false'
        else:
            purchase.recipes.add(recipe)
        return JsonResponse(data)


@login_required(login_url='auth/login/')
def delete_purchase(request, recipe_id):
    if request.method == 'DELETE':
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data = {
            'success': 'true'
        }
        try:
            purchase = Purchase.objects.get(user=request.user)
        except ObjectDoesNotExist:
            data['success'] = 'false'
        try:
            purchase.recipes.remove(recipe)
        except ObjectDoesNotExist:
            data['success'] = 'false'
        return JsonResponse(data)


@login_required(login_url='auth/login/')
def send_shop_list(request):
    if request.method == 'GET':
        purchase = Purchase.objects.get(user=request.user)
        recipes_list = purchase.recipes.all()
        ingredients = recipes_list.values(
            'ingredients__title',
            'ingredients__unit',
            'ingredient__amount'
        )
        filename = f'{settings.MEDIA_ROOT}/shoplists/{purchase.id}_list.txt'
        write_into_file(filename, ingredients)
        shop_file = open(filename, 'rb')
        return FileResponse(shop_file, as_attachment=True)


@login_required(login_url='auth/login/')
def new_recipe(request):
    shop_count = _get_counter(request)
    # GET-запрос на страницу создания рецепта
    if request.method == 'GET':
        form = RecipeForm()
        context = {
            'page_title': 'Создание рецепта',
            'button_label': 'Создать рецепт',
            'shop_count': shop_count,
            'form': form
        }
        return render(request, 'recipe_form.html', context)
    # POST-запрос с данными из формы создания рецепта
    elif request.method == 'POST':
        form = RecipeForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            form.save()
            ingedient_names = request.POST.getlist('nameIngredient')
            products = [Product.objects
                        .get(title=title) for title in ingedient_names]
            amounts = request.POST.getlist('valueIngredient')
            item = Recipe.objects.get(name=form.cleaned_data['name'])
            for i in range(len(amounts)):
                ingredient = Ingredient(
                    recipe=item, ingredient=products[i], amount=amounts[i])
                ingredient.save()
            return redirect('index')
        context = {
            'page_title': 'Создание рецепта',
            'button_label': 'Создать рецепт',
            'shop_count': shop_count,
            'form': form
        }
        return render(request, 'recipe_form.html', context)


@login_required(login_url='auth/login/')
def get_ingredients(request):
    if request.method == 'GET':
        query = unquote(request.GET.get('query'))
        ingredients = Product.objects.filter(title__startswith=query)
        data = [{'title': ingredient.title, 'dimension': ingredient.unit}
                for ingredient in ingredients]
        return JsonResponse(data, safe=False)


@login_required(login_url='auth/login/')
def edit_recipe(request, recipe_id):
    shop_count = _get_counter(request)
    # GET-запрос на страницу редактирования рецепта
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'GET':
        ingredients = recipe.ingredient_set.select_related('ingredient').all()
        form = RecipeForm(instance=recipe)
        context = {
            'recipe_id': recipe_id,
            'page_title': 'Редактирование рецепта',
            'button_label': 'Сохранить',
            'shop_count': shop_count,
            'ingredients': ingredients,
            'form': form
        }
        return render(request, 'recipe_form.html', context)
    # POST-запрос с данными из формы редактирования рецепта
    elif request.method == 'POST':
        form = RecipeForm(request.POST or None,
                          files=request.FILES or None, instance=recipe)
        if form.is_valid():
            form.save()
            old_ingredients = recipe.ingredients.all()
            new_products = request.POST.getlist('nameIngredient')
            new_units = request.POST.getlist('unitsIngredient')
            amounts = request.POST.getlist('valueIngredient')
            products_num = len(new_products)
            new_ingredients = [Product.objects.get(
                title=new_products[i],
                unit=new_units[i]) for i in range(products_num)]
            recipe.ingredients.remove(*old_ingredients)
            for i in range(len(amounts)):
                ingredient = Ingredient(
                    recipe=recipe,
                    ingredient=new_ingredients[i],
                    amount=amounts[i])
                ingredient.save()
            return redirect('index')
        context = {
            'recipe_id': recipe_id,
            'page_title': 'Редактирование рецепта',
            'button_label': 'Сохранить',
            'shop_count': shop_count,
            'ingredients': ingredients,
            'form': form
        }
        return render(request, 'recipe_form.html', context)


@login_required(login_url='auth/login/')
def delete_recipe(request, recipe_id):
    if request.method == 'GET':
        recipe = get_object_or_404(Recipe, id=recipe_id)
        recipe.delete()
        return redirect('index')


def page_not_found(request, exception):
    context = {"path": request.path}
    return render(request, 'misc/404.html', context, status=404)
