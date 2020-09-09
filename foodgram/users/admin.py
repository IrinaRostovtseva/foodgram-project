from django.contrib import admin

from .models import Subscription
from django.contrib.auth import get_user_model


User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('pk', 'username', 'first_name', 'email',)
    list_filter = ('username', 'email',)


admin.site.register(Subscription)
