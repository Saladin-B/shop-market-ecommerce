from django import forms
from subscribers.models import Subscriber


class SubscriberForm(forms.ModelForm):
    """Form for customers to subscribe to shop messages."""
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number',
            'type': 'tel'
        })
    )
    birth_month = forms.IntegerField(
        required=True,
        widget=forms.Select(
            choices=[(i, f'Month {i}') for i in range(1, 13)],
            attrs={'class': 'form-select'}
        )
    )

    class Meta:
        model = Subscriber
        fields = ['birth_month']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['birth_month'] = forms.IntegerField(
            required=True,
            widget=forms.Select(
                choices=[(i, f'Month {i}') for i in range(1, 13)],
                attrs={'class': 'form-select'}
            ),
            label='Birth Month'
        )
