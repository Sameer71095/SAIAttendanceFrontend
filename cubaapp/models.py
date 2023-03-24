from django.db import models
from django import forms

# Create your models here.
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def to_dict(self):
        return {'username': self.cleaned_data['username'], 'password': self.cleaned_data['password']}
    
