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
    # Add username field
    username = forms.CharField(
        max_length=150,
        label=_('Nom d\'utilisateur'),
        widget=forms.TextInput(attrs={
            'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': _('Votre nom d\'utilisateur')
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': _('Nom d\'utilisateur'),
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial value for username
        if self.instance and hasattr(self.instance, 'username'):
            self.fields['username'].initial = self.instance.username

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
                'placeholder': _('+509 XX XX XX XX')
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
            'phone_number': _('Format: +509 XX XX XX XX'),
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
            # Validate that phone number starts with +509 followed by 8 digits
            import re
            if not re.match(r'^\+509\d{8}$', phone_number):
                raise forms.ValidationError(_('Le numéro de téléphone doit commencer par +509 suivi de 8 chiffres.'))
            return phone_number
        return phone_number

class PasswordUpdateForm(forms.Form):
    """
    Form for updating user password.
    """
    old_password = forms.CharField(
        label=_('Ancien mot de passe'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': _('Votre ancien mot de passe')
        })
    )
    new_password1 = forms.CharField(
        label=_('Nouveau mot de passe'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': _('Votre nouveau mot de passe')
        })
    )
    new_password2 = forms.CharField(
        label=_('Confirmer le nouveau mot de passe'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': _('Confirmez votre nouveau mot de passe')
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_('Votre ancien mot de passe est incorrect.'))
        return old_password
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_('Les mots de passe ne correspondent pas.'))
        return password2
    
    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user
