from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, ShopProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class CustomerRegistrationForm(UserCreationForm):
    """Registration form for customers."""
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('username'), Column('email')),
            Row(Column('password1'), Column('password2')),
            Submit('submit', 'Create Account', css_class='btn btn-primary w-100'),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'owner'
        if commit:
            user.save()
        return user