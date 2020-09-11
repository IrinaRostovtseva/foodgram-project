from django.shortcuts import get_object_or_404
from recipes.models import Purchase

def counter(request):
    user = request.user
    counter = Purchase.purchase.counter(user) if user.is_authenticated else None
    return {
        'counter': counter,
    }