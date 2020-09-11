import json
from urllib.parse import unquote

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from users.models import Subscription

from .create_file import write_into_file
from .forms import RecipeForm
from .models import Favorite, Ingredient, Product, Purchase, Recipe, Tag, User


def index(request):
    if request.method != 'GET':
        return HttpResponse(status_code=403)
    tags = request.GET.getlist('tag')
    recipe_list = Recipe.filtration.tag_filter(tags)
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'all_tags': Tag.objects.all(),
        'page': page,
        'paginator': paginator
    }
    user = request.user
    if user.is_authenticated:
        context['active'] = 'recipe'
        context['purchase_list'] = Purchase.purchase.get_purchases_list(user)
        context['favorites'] = Favorite.favorite.get_favorites(user)
    return render(request, 'index.html', context)


def profile(request, user_id):
    if request.method != 'GET':
        return HttpResponse(status_code=403)
    profile = get_object_or_404(User, id=user_id)
    tags = request.GET.getlist('tag')
    recipes_list = Recipe.filtration.tag_filter(tags)
    paginator = Paginator(recipes_list.filter(author=profile), 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'all_tags': Tag.objects.all(),
        'profile': profile,
        'page': page,
        'paginator': paginator
    }
    # Если юзер авторизован, добавляет в контекст список
    # покупок и избранное
    user = request.user
    if user.is_authenticated:
        context['is_subscribed'] = Subscription.objects.filter(
            user=request.user, author=profile).exists()
        context['purchase_list'] = Purchase.purchase.get_purchases_list(user)
        context['favorites'] = Favorite.favorite.get_favorites(user)
    return render(request, 'profile.html', context)


def recipe_detail(request, recipe_id):
    if request.method != 'GET':
        return HttpResponse(status_code=403)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    author = recipe.author
    context = {
        'recipe': recipe,
    }
    user = request.user
    if user.is_authenticated:
        is_subscribed = Subscription.objects.filter(
            user=user, author=author).exists()
        try:
            is_favorite = Favorite.objects.get(
                user=user).recipes.filter(id=recipe_id).exists()
        except ObjectDoesNotExist:
            is_favorite = False
        try:
            is_purchased = Purchase.objects.get(
                user=user).recipes.filter(id=recipe_id).exists()
        except ObjectDoesNotExist:
            is_purchased = False
        context['is_subscribed'] = is_subscribed
        context['is_favorite'] = is_favorite
        context['is_purchased'] = is_purchased
    return render(request, 'recipe_detail.html', context)


class FavoriteView(View):
    model = Favorite

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        user = get_object_or_404(User, id=self.request.user.id)
        queryset = self.model.favorite.get_favorites(user)
        return queryset

    def get(self, request):
        paginator = Paginator(self.get_queryset(), 6)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        purchase_list = Purchase.purchase.get_purchases_list(request.user)
        context = {
            'all_tag': Tag.objects.all(),
            'favorites': page,
            'purchase_list': purchase_list,
            'active': 'favorite',
            'paginator': paginator,
            'page': page
        }
        return render(request, 'favorites.html', context)

    def post(self, request):
        user = get_object_or_404(User, id=request.user.id)
        json_data = json.loads(request.body.decode())
        recipe_id = int(json_data['id'])
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data = {'success': 'true'}
        favorite = Favorite.favorite.get_user(user)
        is_favorite = favorite.recipes.filter(id=recipe_id).exists()
        if is_favorite:
            data['success'] = 'false'
        else:
            favorite.recipes.add(recipe)
        return JsonResponse(data)


@login_required(login_url='auth/login/')
def delete_favorite(request, recipe_id):
    if request.method != 'DELETE':
        return HttpResponse(status_code=403)
    user = get_object_or_404(User, username=request.user.username)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    data = {'success': 'true'}
    try:
        favorite = Favorite.objects.get(user=user)
        favorite.recipes.remove(recipe)
    except ObjectDoesNotExist:
        data['success'] = 'false'
    return JsonResponse(data)


@login_required(login_url='auth/login/')
def get_subscriptions(request):
    if request.method != 'GET':
        return HttpResponse(status_code=403)
    auth_user = get_object_or_404(User, username=request.user.username)
    try:
        subscriptions = Subscription.objects.filter(user=auth_user)
    except ObjectDoesNotExist:
        subscriptions = []
    page_num = request.GET.get('page')
    paginator = Paginator(subscriptions, 6)
    page = paginator.get_page(page_num)
    context = {
        'active': 'subscription',
        'paginator': paginator,
        'page': page,
    }
    return render(request, 'subscriptions.html', context)


@login_required(login_url='auth/login/')
def subscription(request):
    if request.method != 'POST':
        return HttpResponse(status_code=403)
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
    if request.method != 'DELETE':
        return HttpResponse(status_code=403)
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


class PurchaseView(View):
    model = Purchase

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        user = get_object_or_404(User, id=self.request.user.id)
        queryset = self.model.purchase.get_purchases_list(user)
        return queryset

    def get(self, request):
        recipes_list = self.get_queryset()
        context = {
            'recipes_list': recipes_list,
            'active': 'purchase'
        }
        return render(request, 'purchases.html', context)

    def post(self, request):
        json_data = json.loads(request.body.decode())
        recipe_id = int(json_data['id'])
        user = get_object_or_404(User, id=request.user.id)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        purchase = Purchase.purchase.get_user_purchase(user=user)
        data = {
            'success': 'true'
        }
        if not purchase.recipes.filter(id=recipe_id).exists():
            purchase.recipes.add(recipe)
            return JsonResponse(data)
        data['success'] = 'false'
        return JsonResponse(data)


@login_required(login_url='auth/login/')
def delete_purchase(request, recipe_id):
    if request.method != 'DELETE':
        return HttpResponse(status_code=403)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    data = {
        'success': 'true'
    }
    try:
        purchase = Purchase.objects.get(user=request.user)
        purchase.recipes.remove(recipe)
    except ObjectDoesNotExist:
        data['success'] = 'false'
    return JsonResponse(data)


@login_required(login_url='auth/login/')
def send_shop_list(request):
    if request.method != 'GET':
        return HttpResponse(status_code=403)
    user = request.user
    ingredients = (Ingredient.objects
                   .select_related('ingredient')
                   .filter(recipe__purchase__user=user)
                   .values('ingredient__title', 'ingredient__unit')
                   .annotate(Sum('amount'))
                   )
    filename = f'{settings.MEDIA_ROOT}/shoplists/{user.id}_list.txt'
    write_into_file(filename, ingredients)
    shop_file = open(filename, 'rb')
    return FileResponse(shop_file, as_attachment=True)


@login_required(login_url='auth/login/')
def new_recipe(request):
    context = {
        'active': 'new_recipe',
        'page_title': 'Создание рецепта',
        'button_label': 'Создать рецепт',
    }
    # GET-запрос на страницу создания рецепта
    if request.method == 'GET':
        form = RecipeForm()
        context['form'] = form
        return render(request, 'recipe_form.html', context)
    # POST-запрос с данными из формы создания рецепта
    elif request.method == 'POST':
        form = RecipeForm(request.POST, files=request.FILES or None)
        if not form.is_valid():
            context['form'] = form
            return render(request, 'recipe_form.html', context)
        recipe = form.save(commit=False)
        recipe.author = request.user
        form.save()
        ingedient_names = request.POST.getlist('nameIngredient')
        ingredient_units = request.POST.getlist('unitsIngredient')
        amounts = request.POST.getlist('valueIngredient')
        products = [Product.objects.get(
            title=ingedient_names[i],
            unit=ingredient_units[i]
        ) for i in range(len(ingedient_names))]
        ingredients = []
        for i in range(len(amounts)):
            ingredients.append(Ingredient(
                recipe=recipe, ingredient=products[i], amount=amounts[i]))
        Ingredient.objects.bulk_create(ingredients)
        return redirect('index')


@login_required(login_url='auth/login/')
def get_ingredients(request):
    if request.method != 'GET':
        return HttpResponse(status_code=403)
    query = unquote(request.GET.get('query'))
    ingredients = Product.objects.filter(title__startswith=query)
    data = [{'title': ingredient.title, 'dimension': ingredient.unit}
            for ingredient in ingredients]
    return JsonResponse(data, safe=False)


@login_required(login_url='auth/login/')
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {
        'recipe_id': recipe_id,
        'page_title': 'Редактирование рецепта',
        'button_label': 'Сохранить',
    }
    # GET-запрос на страницу редактирования рецепта
    if request.method == 'GET':
        form = RecipeForm(instance=recipe)
        context['form'] = form
        return render(request, 'recipe_form.html', context)
    # POST-запрос с данными из формы редактирования рецепта
    elif request.method == 'POST':
        form = RecipeForm(request.POST or None,
                          files=request.FILES or None, instance=recipe)
        if not form.is_valid():
            context['form'] = form
            return render(request, 'recipe_form.html', context)
        form.save()
        new_titles = request.POST.getlist('nameIngredient')
        new_units = request.POST.getlist('unitsIngredient')
        amounts = request.POST.getlist('valueIngredient')
        products_num = len(new_titles)
        new_ingredients = []
        Ingredient.objects.filter(recipe__id=recipe_id).delete()
        for i in range(products_num):
            product = Product.objects.get(
                title=new_titles[i], unit=new_units[i])
            new_ingredients.append(Ingredient(recipe=recipe,
                                              ingredient=product,
                                              amount=amounts[i]))
        Ingredient.objects.bulk_create(new_ingredients)
        return redirect('index')


@login_required(login_url='auth/login/')
def delete_recipe(request, recipe_id):
    if request.method != 'GET':
        return HttpResponse(status_code=403)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.delete()
    return redirect('index')


def page_not_found(request, exception):
    context = {'path': request.path}
    return render(request, 'misc/404.html', context, status=404)
