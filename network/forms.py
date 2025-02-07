from django.forms import ModelForm
from django import forms
from .models import *

class EditProfile(ModelForm):
    class Meta:
        model = User
        fields = ['name', 'bio', 'link', 'profile_pic', 'header_pic']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'content w-100 mb-3', 'id': 'edit-name', 'placeholder': 'Name'}),
            'profile_pic': forms.FileInput(attrs={'class': 'content form-control mb-3', 'id': 'edit-pic'}),
            'header_pic': forms.FileInput(attrs={'class': 'content form-control mb-3', 'id': 'edit-header'}),
            'bio': forms.Textarea(attrs={'class': 'content form-control mb-3', 'id': 'edit-bio', 'placeholder': 'Bio'}),
            'link': forms.TextInput(attrs={'class': 'content form-control mb-3', 'id': 'edit-link', 'placeholder': 'Link'})
        }