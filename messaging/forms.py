from django import forms
from subscribers.models import Subscriber, MONTH_CHOICES
from .models import Message, MessageTemplate


class SubscriberForm(forms.ModelForm):
    """Form for customers to subscribe to shop messages."""
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+44 7700 900 123',
            'type': 'tel'
        })
    )
    birth_month = forms.ChoiceField(
        required=True,
        choices=MONTH_CHOICES,
        widget=forms.Select(
            attrs={'class': 'form-select'}
        )
    )

    class Meta:
        model = Subscriber
        fields = ['birth_month']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['birth_month'] = forms.ChoiceField(
            required=True,
            choices=MONTH_CHOICES,
            widget=forms.Select(
                attrs={'class': 'form-select'}
            ),
            label='Birth Month'
        )


class MessageForm(forms.ModelForm):
    """Form for shop owners to compose and send messages to subscribers."""
    use_template = forms.ModelChoiceField(
        queryset=MessageTemplate.objects.none(),
        required=False,
        label='Use Template (Optional)',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Message
        fields = ['content', 'message_type', 'scheduled_for']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your message (max 1600 characters)',
                'rows': 6,
                'maxlength': 1600
            }),
            'message_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'scheduled_for': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }
        labels = {
            'content': 'Message Content',
            'message_type': 'Send Via',
            'scheduled_for': 'Schedule For (Leave blank to send now)'
        }
    
    def __init__(self, *args, **kwargs):
        shop_profile = kwargs.pop('shop_profile', None)
        super().__init__(*args, **kwargs)
        
        # Set templates queryset if shop_profile provided
        if shop_profile:
            self.fields['use_template'].queryset = MessageTemplate.objects.filter(
                shop_profile=shop_profile
            )
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) == 0:
            raise forms.ValidationError('Message content cannot be empty.')
        if len(content) > 1600:
            raise forms.ValidationError('Message is too long (max 1600 characters).')
        return content
