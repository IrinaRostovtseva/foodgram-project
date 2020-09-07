import json
from urllib.parse import unquote

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.edit import FormView
from users.models import Subscription

from .create_file import write_into_file
from .forms import RecipeForm
from .models import Favorite, Purchase, Recipe, User, Product, Ingredient, Tag


def index(request):
    tag = request.GET.get('tag', None)
    if tag is not None:
        recipe_list = Recipe.objects.filter(
            tags__slug=tag).order_by('-pub_date')
    else:
        recipe_list = Recipe.objects.order_by('-pub_date')
    paginator = Paginator(recipe_list, 3)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'tag': tag,
        'page': page,
        'paginator': paginator
    }
    if request.user.is_authenticated:
        purchase = Purchase.objects.get(user=request.user)
        shop_count = purchase.recipes.count()
        favorite = get_object_or_404(Favorite, user=request.user)
        context['favorites'] = favorite.recipes.all()
        context['shop_count'] = shop_count
    return render(request, 'index.html', context)


def profile(request, user_id):
    if request.method == 'GET':
        tag = request.GET.get('tag')
        profile = get_object_or_404(User, id=user_id)
        favorite = get_object_or_404(Favorite, user=request.user)
        is_subscribed = Subscription.objects.filter(user__id=user_id, author=profile).exists()
        if tag is None:
            recipes_list = Recipe.objects.filter(
                author__id=user_id).order_by('-pub_date')
        else:
            recipes_list = Recipe.objects.filter(
                author__id=user_id, tags__slug=tag).order_by('-pub_date')
        paginator = Paginator(recipes_list, 3)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        context = {
            'profile': profile,
            'is_subscribed': is_subscribed,
            'page': page,
            'paginator': paginator
        }
        if request.user.is_authenticated:
            favorite = get_object_or_404(Favorite, user=request.user)
            purchase = Purchase.objects.get(user=request.user)
            shop_count = purchase.recipes.count()
            context['favorites'] = favorite.recipes.all()
            context['shop_count'] = shop_count
        return render(request, 'profile.html', context)


def recipe_detail(request, recipe_id):
    if request.method == 'GET':
        recipe = get_object_or_404(Recipe, id=recipe_id)
        author = recipe.author
        context = {
            'recipe': recipe,
        }
        if request.user.is_authenticated:
            is_subscribed = Subscription.objects.filter(
                user=request.user, author=author)
            favorite = Favorite.objects.get(user=request.user)
            is_favorite = favorite.recipes.filter(id=recipe_id)
            purchase = Purchase.objects.get(user=request.user)
            shop_count = purchase.recipes.count()
            context['is_subscribed'] = is_subscribed
            context['is_favorite'] = is_favorite
            context['shop_count'] = shop_count
        return render(request, 'recipe_detail.html', context)


@login_required
def favorite(request):
    if request.method == 'GET':
        tag = request.GET.get('tag')
        auth_user = get_object_or_404(User, username=request.user.username)
        favorite = Favorite.objects.get(user=auth_user)
        if tag is None:
            recipes_list = favorite.recipes.all().order_by('pub_date')
        else:
            recipes_list = favorite.recipes.filter(
                tags__slug=tag).order_by('pub_date')
        purchase = Purchase.objects.get(user=request.user)
        shop_count = purchase.recipes.count()
        paginator = Paginator(recipes_list, 3)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        context = {
            'tag': tag,
            'favorites': favorite.recipes.all(),
            'shop_count': shop_count,
            'paginator': paginator,
            'page': page
        }
        return render(request, 'favorites.html', context)
    elif request.method == 'POST':
        json_data = json.loads(request.body.decode())
        recipe_id = int(json_data['id'])
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, id=request.user.id)
        is_exist = Favorite.objects.filter(user=user).exists()
        data = {'success': 'true'}
        if not is_exist:
            favorite = Favorite(user=user)
            favorite.save()
            favorite.recipes.add(recipe)
        else:
            favorite = Favorite.objects.get(user=user)
            is_favorite = favorite.recipes.filter(id=recipe_id).exists()
            if is_favorite:
                data['success'] = 'false'
            else:
                favorite.recipes.add(recipe)
        return JsonResponse(data)


@login_required
def delete_favorite(request, recipe_id):
    if request.method == 'DELETE':
        user = get_object_or_404(User, username=request.user.username)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        is_exist = Favorite.objects.filter(user=user).exists()
        data = {'success': 'true'}
        if not is_exist:
            data['success'] = 'false'
        else:
            favorite = Favorite.objects.get(user=user)
            if favorite.recipes.filter(id=recipe_id).exists():
                data['success'] = 'false'
            else:
                favorite.recipes.remove(recipe)
        return JsonResponse(data)


@login_required
def get_subscriptions(request):
    if request.method == 'GET':
        auth_user = get_object_or_404(User, username=request.user.username)
        subscriptions = Subscription.objects.filter(user=auth_user)
        purchase = Purchase.objects.get(user=request.user)
        shop_count = purchase.recipes.count()
        page_num = request.GET.get('page')
        paginator = Paginator(subscriptions, 3)
        page = paginator.get_page(page_num)
        context = {
            'shop_count': shop_count,
            'paginator': paginator,
            'page': page,
        }
        return render(request, 'subscriptions.html', context)


@login_required
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


@login_required
def delete_subscription(request, author_id):
    if request.method == 'DELETE':
        auth_user = get_object_or_404(User, id=request.user.id)
        author = get_object_or_404(User, id=author_id)
        is_exist = Subscription.objects.filter(
            user=auth_user, author=author).exists()
        data = {'success': 'true'}
        if not is_exist:
            data['success'] = 'false'
        else:
            follow = Subscription.objects.filter(
                user=auth_user, author=author)
            follow.delete()
        return JsonResponse(data)


@login_required
def purchase(request):
    if request.method == 'GET':
        user = get_object_or_404(User, id=request.user.id)
        is_list_exist = Purchase.objects.filter(user=user).exists()
        purchase = Purchase.objects.get(user=request.user)
        shop_count = purchase.recipes.count()
        context = {'shop_count': shop_count}
        if is_list_exist:
            purchase = Purchase.objects.get(user=user)
            recipes_list = purchase.recipes.all()
            context['recipes_list'] = recipes_list
        return render(request, 'purchases.html', context)
    if request.method == 'POST':
        json_data = json.loads(request.body.decode())
        recipe_id = int(json_data['id'])
        user = get_object_or_404(User, id=request.user.id)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        is_exist = Purchase.objects.filter(user=user).exists()
        data = {
            'success': 'true'
        }
        if is_exist:
            purchase = Purchase.objects.get(user=user)
            if purchase.recipes.filter(id=recipe_id).exists():
                data['success'] = 'false'
            else:
                purchase.recipes.add(recipe)
        else:
            purchase = Purchase(user=user)
            purchase.save()
            purchase.recipes.add(recipe)
        return JsonResponse(data)


@login_required
def delete_purchase(request, recipe_id):
    if request.method == 'DELETE':
        recipe = get_object_or_404(Recipe, id=recipe_id)
        is_exist = Purchase.objects.filter(user=request.user).exists()
        data = {
            'success': 'true'
        }
        if not is_exist:
            data['success'] = 'false'
        else:
            purchase = Purchase.objects.get(user=request.user)
            is_recipe_exist = purchase.recipes.filter(id=recipe_id).exists()
            if is_recipe_exist:
                purchase.recipes.remove(recipe)
            else:
                data['success'] = 'false'
        return JsonResponse(data)


@login_required
def send_shop_list(request):
    if request.method == 'GET':
        user = get_object_or_404(User, id=request.user.id)
        purchase = Purchase.objects.get(user=user)
        recipes_list = purchase.recipes.all()
        ingredients = recipes_list.values(
            'ingredients__title', 'ingredients__unit').annotate(Sum('ingredient__amount'))
        filename = f'{settings.MEDIA_ROOT}/shoplists/{purchase.id}_shoplist.txt'
        write_into_file(filename, ingredients)
        shop_file = open(filename, 'rb')
        return FileResponse(shop_file, as_attachment=True)


@login_required
def new_recipe(request):
    if request.method == 'GET':
        form = RecipeForm()
        context = {
            'page_title': 'Создание рецепта',
            'button_label': 'Создать рецепт',
            'form': form
        }
        return render(request, 'recipe_form.html', context)
    elif request.method == 'POST':
        form = RecipeForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            form.save()
            products = [Product.objects.get(
                title=title) for title in request.POST.getlist('nameIngredient')]
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
            'form': form
        }
        return render(request, 'recipe_form.html', context)


@login_required
def get_ingredients(request):
    if request.method == 'GET':
        query = unquote(request.GET.get('query'))
        ingredients = Product.objects.filter(title__startswith=query)
        data = [{'title': ingredient.title, 'dimension': ingredient.unit}
                for ingredient in ingredients]
        return JsonResponse(data, safe=False)


@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    ingredients = recipe.ingredient_set.all()
    if request.method == 'GET':
        form = RecipeForm(instance=recipe)
        context = {
            'recipe_id': recipe_id,
            'page_title': 'Редактирование рецепта',
            'button_label': 'Сохранить',
            'ingredients': ingredients,
            'form': form
        }
        return render(request, 'recipe_form.html', context)
    elif request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES or None, instance=recipe)
        if form.is_valid():
            form.save()
            ing_set = set(ingredients)
            new_ing = {Product.objects.get(
                title=name) for name in request.POST.getlist('nameIngredient')}
            ing_to_add = list(new_ing.difference(ing_set))
            ing_to_delete = list(ing_set.difference(new_ing))
            amounts = request.POST.getlist('valueIngredient')
            for i in range(len(amounts)):
                ingredient = Ingredient(
                    recipe=recipe, ingredient=ing_to_add[i], amount=amounts[i])
                ingredient.save()
            recipe.ingredients.remove(*ing_to_delete)
            return redirect('index')


@login_required
def delete_recipe(request, recipe_id):
    if request.method == 'GET':
        recipe = get_object_or_404(Recipe, id=recipe_id)
        recipe.delete()
        return redirect('index')
