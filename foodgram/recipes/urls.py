from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<int:user_id>', views.profile, name='profile'),
    path('favorites', views.favorite, name='favorite'),
    path('favorites/<int:recipe_id>', views.delete_favorite,
         name='delete_favorite'),
    path('my_subscriptions', views.get_subscriptions, name='my_subscriptions'),
    path('subscriptions', views.subscription, name='subscription'),
    path('subscriptions/<int:recipe_id>', views.delete_subscription,
         name='delete_subscription'),
    path('recipes/new', views.new_recipe, name='new_recipe'),
    path('recipes/<int:recipe_id>', views.recipe_detail,
         name='recipe'),
    # path('recipes/<int:recipe>/edit', views.edit_recipe, name='edit_recipe'),
    path('purchases', views.purchase, name='purchases'),
    path('purchases/<int:recipe_id>', views.delete_purchase,
         name='delete_purchase'),
    path('shoplist', views.send_shop_list, name='shop-list'),
    path('ingredients', views.get_ingredients, name='ingredients'),
]
