from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, ShopProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class BuyerRegistrationForm(UserCreationForm):
    """Registration form for buyers/customers."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True, label='First Name')
    last_name = forms.CharField(max_length=150, required=True, label='Last Name')

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('first_name'), Column('last_name')),
            Row(Column('username'), Column('email')),
            Row(Column('password1'), Column('password2')),
            Submit('submit', 'Create Buyer Account', css_class='btn btn-primary w-100'),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'
        if commit:
            user.save()
        return user


class ShopOwnerRegistrationForm(UserCreationForm):
    """Registration form for shop owners."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True, label='First Name')
    last_name = forms.CharField(max_length=150, required=True, label='Last Name')
    shop_name = forms.CharField(max_length=255, required=True, label='Shop Name')

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'shop_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('first_name'), Column('last_name')),
            Row(Column('username'), Column('email')),
            'shop_name',
            Row(Column('password1'), Column('password2')),
            Submit('submit', 'Create Shop Account', css_class='btn btn-primary w-100'),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'shop_owner'
        if commit:
            user.save()
            # Create shop profile for owner
            shop_name = self.cleaned_data.get('shop_name')
            ShopProfile.objects.create(owner=user, shop_name=shop_name)
        return user


# Keep old name for backwards compatibility
CustomerRegistrationForm = BuyerRegistrationForm