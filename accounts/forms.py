from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class SignUpForm(UserCreationForm):
    address = forms.CharField(max_length=255, required=False, help_text='Optional.')
    phone_number = forms.CharField(max_length=20, required=False, help_text='Optional.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'address', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserProfile.objects.get_or_create(user=user, defaults={'address': self.cleaned_data['address'],     'phone_number': self.cleaned_data['phone_number']})
        return user

