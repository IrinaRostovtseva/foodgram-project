from django.contrib.auth import get_user_model
from django import forms


User = get_user_model()


class CreationForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'username', 'email', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
