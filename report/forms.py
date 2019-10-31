from django.contrib.auth.models import User
from django import forms


class ReportForm(forms.ModelForm):
    username = forms.CharField(
        label='Логин'
    )

    password1 = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput,
        strip=False
    )

    class Meta:
        model = User
        fields = ('username',)
