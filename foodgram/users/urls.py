from django.urls import path
from users import views

from .views import SignUp

urlpatterns = [
    path('signup', SignUp.as_view(), name='signup'),
]
