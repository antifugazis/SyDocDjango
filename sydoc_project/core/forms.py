from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from .models import Profile
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class UserUpdateForm(UserChangeForm):
    """
    Form for updating basic user information.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': _('Prénom'),
            'last_name': _('Nom'),
            'email': _('Adresse email'),
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': _('Votre prénom')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': _('Votre nom')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': _('votre@email.com')
            }),
        }

class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating profile information.
    """
    class Meta:
        model = Profile
        fields = ['profile_picture', 'establishment_name', 'phone_number', 'date_of_birth', 'bio']
        labels = {
            'profile_picture': _('Photo de profil'),
            'establishment_name': _("Nom de l'établissement"),
            'phone_number': _('Téléphone'),
            'date_of_birth': _('Date de naissance'),
            'bio': _('À propos de moi'),
        }
        widgets = {
            'establishment_name': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': _("Nom de votre établissement")
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': _('+225 XX XX XX XX')
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-textarea mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'rows': 4,
                'placeholder': _('Parlez-nous un peu de vous...')
            }),
        }
        help_texts = {
            'phone_number': _('Format: +225 XX XX XX XX'),
            'profile_picture': _('Téléchargez une image de profil (format JPG, PNG)'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional
        for field in self.fields:
            self.fields[field].required = False
            
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Remove any non-digit characters except +
            cleaned_phone = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            return cleaned_phone
        return phone_number
