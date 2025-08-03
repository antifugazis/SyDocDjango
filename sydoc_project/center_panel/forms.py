# sydoc_project/center_panel/forms.py

from django import forms
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from core.models import LiteraryGenre, SubGenre, Theme, SousTheme, Book, BookVolume, Author, Member, Loan, Staff, Activity, ArchivalDocument, TrainingSubject, TrainingModule, Lesson, Question, Answer, Communique, Role, Profile, BookDigitization, DigitizedPage, Language, DeletedBook
from .models import AgeVerificationFailure, Complaint
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm

class BookForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.documentation_center = kwargs.pop('documentation_center', None)
        super().__init__(*args, **kwargs)
        
        # Add Tailwind CSS classes to all form fields for consistent styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        
        # Special styling for checkbox fields
        self.fields['is_digital'].widget.attrs['class'] = 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
        self.fields['has_volumes'].widget.attrs['class'] = 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
        
        # Limit choices to the current documentation center if provided
        if self.documentation_center:
            self.fields['literary_genre'].queryset = LiteraryGenre.objects.all()
            self.fields['sub_genre'].queryset = SubGenre.objects.filter(genre__in=self.fields['literary_genre'].queryset)
            self.fields['theme'].queryset = Theme.objects.all()
            self.fields['sub_theme'].queryset = SousTheme.objects.filter(theme__in=self.fields['theme'].queryset)
            
        # Set language queryset with favorites first
        self.fields['language'].queryset = Language.objects.all().order_by('-is_favorite', 'name')
        
        # Add empty labels for select fields
        self.fields['literary_genre'].empty_label = 'Sélectionner un genre'
        self.fields['sub_genre'].empty_label = 'Sélectionner un sous-genre (optionnel)'
        self.fields['theme'].empty_label = 'Sélectionner un thème (optionnel)'
        self.fields['sub_theme'].empty_label = 'Sélectionner un sous-thème (optionnel)'
    
    class Meta:
        model = Book
        fields = [
            'title', 'isbn', 'publication_date', 'authors', 'editor', 'description',
            'literary_genre', 'sub_genre', 'theme', 'sub_theme',
            'is_digital', 'file_upload', 'pages', 'quantity_available',
            'total_quantity', 'acquisition_date', 'cover_image', 'price',
            'status', 'language', 'minimum_age_required', 'has_volumes', 'volume_count'
        ]
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'acquisition_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'title': 'Titre du Livre',
            'isbn': 'ISBN',
            'publication_date': 'Date de Publication',
            'authors': 'Auteur(s)',
            'editor': 'Éditeur',
            'description': 'Description',
            'literary_genre': 'Genre Littéraire',
            'sub_genre': 'Sous-Genre',
            'theme': 'Thème Principal',
            'sub_theme': 'Sous-Thème',
            'is_digital': 'Version Numérique Disponible',
            'file_upload': 'Fichier Numérique (PDF, EPUB, etc.)',
            'pages': 'Nombre de Pages',
            'quantity_available': 'Quantité Disponible (Physique)',
            'total_quantity': 'Quantité Totale (Physique)',
            'acquisition_date': "Date d'Acquisition",
            'cover_image': 'Image de Couverture',
            'price': 'Prix (Gourdes)',
            'status': 'Statut du livre',
            'language': 'Langue',
            'minimum_age_required': 'Âge Minimum Requis',
            'has_volumes': 'Possède des Tomes/Volumes',
            'volume_count': 'Nombre de Tomes/Volumes'
        }

class BookVolumeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Tailwind CSS classes to all form fields for consistent styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
    
    class Meta:
        model = BookVolume
        fields = [
            'volume_number', 'title', 'quantity_available', 'total_quantity',
            'price', 'cover_image', 'pages'
        ]
        widgets = {
            'cover_image': forms.FileInput(),
        }
        labels = {
            'volume_number': 'Numéro du Tome',
            'title': 'Titre du Tome',
            'quantity_available': 'Quantité Disponible',
            'total_quantity': 'Quantité Totale',
            'price': 'Prix (Gourdes)',
            'cover_image': 'Image de Couverture',
            'pages': 'Nombre de Pages'
        }


# Create a formset for BookVolume
BookVolumeFormSet = inlineformset_factory(
    Book, 
    BookVolume,
    form=BookVolumeForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)


class LoanForm(forms.ModelForm):
    """Enhanced loan form with age verification"""
    # Add a field for age verification that's not in the model
    member_age_verification = forms.IntegerField(
        label="Âge du membre",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'})
    )
    
    class Meta:
        model = Loan
        fields = [
            'book', 'member', 'loan_date', 'due_date',
            'age_verified', 'quantity'
        ]
        widgets = {
            'loan_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'age_verified': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }
        labels = {
            'book': 'Livre',
            'member': 'Membre',
            'loan_date': "Date d'emprunt",
            'due_date': 'Date de retour prévue',
            'age_verified': 'Âge vérifié',
            'quantity': 'Quantité'
        }
    
    def __init__(self, *args, **kwargs):
        self.documentation_center = kwargs.pop('documentation_center', None)
        super().__init__(*args, **kwargs)
        
        # Add Tailwind CSS classes to all form fields for consistent styling
        for field_name, field in self.fields.items():
            if field_name != 'age_verified':
                field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        
        # Filter books by documentation center
        if self.documentation_center:
            self.fields['book'].queryset = Book.objects.filter(
                documentation_center=self.documentation_center,
                status='available'
            ).order_by('title')
            self.fields['member'].queryset = Member.objects.filter(
                documentation_center=self.documentation_center,
                is_active=True
            ).order_by('last_name', 'first_name')
        
        # No volume field needed anymore
    
    # Add a field for temporary date of birth
    temp_date_of_birth = forms.DateField(
        label="Date de naissance temporaire",
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        })
    )
    
    def clean(self):
        import logging
        from datetime import date
        logger = logging.getLogger(__name__)
        
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        member = cleaned_data.get('member')
        age_verified = cleaned_data.get('age_verified')
        temp_date_of_birth = cleaned_data.get('temp_date_of_birth')
        
        # Debug logging
        logger.info(f"LoanForm clean() - Book: {book}, Member: {member}")
        if book:
            logger.info(f"Book min_age: {book.minimum_age_required}")
        
        # Skip validation if essential fields are missing
        if not book or not member:
            logger.info("Skipping validation - missing book or member")
            return cleaned_data
        
        # Age verification checks - only if minimum age is actually required
        if book and book.minimum_age_required and book.minimum_age_required > 0:
            # If member doesn't have date_of_birth but temp_date_of_birth is provided, use it
            use_date_of_birth = member.date_of_birth
            if not use_date_of_birth and temp_date_of_birth:
                use_date_of_birth = temp_date_of_birth
                # Update the member with this date of birth for future use
                member.date_of_birth = temp_date_of_birth
                member.save(update_fields=['date_of_birth'])
                logger.info(f"Updated member {member.id} with date of birth: {temp_date_of_birth}")
            
            # Calculate member's actual age from date_of_birth
            if use_date_of_birth:
                today = date.today()
                member_age = today.year - use_date_of_birth.year - ((today.month, today.day) < (use_date_of_birth.month, use_date_of_birth.day))
                # Store the age in a variable but don't add to cleaned_data since it's not a form field
                logger.info(f"Age verification needed. Verified: {age_verified}, Calculated Age: {member_age}")
                self.calculated_member_age = member_age
                
                # If member's age meets the requirement, we can auto-verify
                if member_age >= book.minimum_age_required:
                    logger.info(f"Member age {member_age} >= required age {book.minimum_age_required}, auto-verifying")
                    cleaned_data['age_verified'] = True
                    logger.info(f"Auto-verified age. New age_verified value: {cleaned_data.get('age_verified')}")
                else:
                    logger.info(f"Member age {member_age} < required age {book.minimum_age_required}, showing error")
                    self.add_error('age_verified', f"Le membre doit avoir au moins {book.minimum_age_required} ans pour emprunter ce livre. Âge actuel: {member_age} ans.")
                    
                    # Still require manual verification in case of special exceptions
                    # Check the updated value in cleaned_data, not the original age_verified variable
                    if not cleaned_data.get('age_verified', False):
                        self.add_error('age_verified', "L'âge du membre doit être vérifié pour ce livre.")
            else:
                self.add_error('temp_date_of_birth', "Veuillez fournir une date de naissance temporaire pour ce membre afin de vérifier l'âge requis pour ce livre.")
        
        # Check if the book is available
        quantity = cleaned_data.get('quantity', 1)
        if not quantity or quantity < 1:
            quantity = 1
            cleaned_data['quantity'] = 1
        
        logger.info(f"Quantity check: {quantity}")
        
        # Check book availability
        if book and hasattr(book, 'quantity_available'):
            logger.info(f"Book quantity available: {book.quantity_available}")
            if book.quantity_available < quantity:
                self.add_error('quantity', f"Seulement {book.quantity_available} exemplaires disponibles pour ce livre.")
        
        # Log any form errors
        if self.errors:
            logger.error(f"Form validation errors: {self.errors}")
        
        return cleaned_data
        
    def _update_errors(self, errors):
        """Override to handle model validation errors that reference fields not in the form"""
        # Handle model validation errors that reference fields not in the form
        if hasattr(errors, 'error_dict'):
            # Make a copy of the error_dict to avoid modifying the original
            error_dict = errors.error_dict.copy()
            errors.error_dict = {}
            
            for field, field_errors in error_dict.items():
                # If the field doesn't exist in the form, add the error to a related field
                if field not in self.fields:
                    if field == 'member_age':
                        # Add member_age errors to age_verified field
                        for error in field_errors:
                            self.add_error('age_verified', error)
                    else:
                        # For other fields, add to non-field errors
                        for error in field_errors:
                            self.add_error(None, error)
                else:
                    # Add error to the appropriate field
                    for error in field_errors:
                        self.add_error(field, error)
        else:
            # Call the parent method for non-dict validation errors
            super()._update_errors(errors)
            
    def _post_clean(self):
        """Override to handle model validation errors that reference fields not in the form"""
        # Set member_age before model validation runs
        if hasattr(self, 'calculated_member_age'):
            self.instance.member_age = self.calculated_member_age
        
        # Call the parent _post_clean to perform model validation
        super()._post_clean()
        
    def save(self, commit=True):
        """Save the form and set the member_age field if available"""
        loan = super().save(commit=False)
        
        # Set the member_age field if we calculated it
        if hasattr(self, 'calculated_member_age'):
            loan.member_age = self.calculated_member_age
        
        if commit:
            loan.save()
            
        return loan


class LoanCancellationForm(forms.Form):
    """Form for cancelling a loan"""
    cancellation_reason = forms.ChoiceField(
        choices=Loan.CANCELLATION_REASONS,
        label="Raison d'annulation",
        widget=forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'})
    )
    cancellation_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        label="Notes d'annulation",
        required=False
    )


class DeletedBookRestoreForm(forms.Form):
    """Form for restoring a book from the trash"""
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        label='Raison de la restauration',
        required=False
    )


class MemberForm(forms.ModelForm):
    USER_TYPE_CHOICES = [
        ('Super Admin', 'Super Admin'),
        ('Admin', 'Admin'),
        ('Documentation Center', 'Documentation Center'),
        ('Member', 'Member'),
    ]
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        label='Type d\'utilisateur',
        required=True,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        })
    )
    
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        }),
        required=True
    )
    
    confirm_password = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        }),
        required=True
    )
    
    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'address',
            'date_of_birth', 'membership_type', 'is_active'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'required': 'required'}),
            'membership_type': forms.Select(choices=Member.MEMBERSHIP_CHOICES),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'})
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'E-mail',
            'phone_number': 'Téléphone',
            'address': 'Adresse',
            'date_of_birth': 'Date de Naissance (obligatoire)',
            'membership_type': 'Type d\'adhésion',
            'is_active': 'Actif',
        }
        
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if not date_of_birth:
            raise forms.ValidationError('La date de naissance est obligatoire pour vérifier l\'âge lors des emprunts de livres.')
        return date_of_birth

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply consistent Tailwind CSS classes
        for field_name, field in self.fields.items():
            if field_name not in ['is_active', 'user_type', 'password', 'confirm_password']:  # Skip fields with custom classes
                field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Les mots de passe ne correspondent pas.')
        
        return cleaned_data

class CreateLoanForm(forms.Form):
    """
    This form is used to initiate a loan by selecting a member and books.
    """
    member = forms.ModelChoiceField(
        queryset=Member.objects.none(), # We will set this in the view
        label="Initiateur du prêt",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    books = forms.ModelMultipleChoiceField(
        queryset=Book.objects.none(), # We will also set this in the view
        label="Ouvrage(s) à prêter",
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    due_date = forms.DateField(
        label="Date de retour prévue",
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, center, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate dropdowns with active members and available books for the specific center
        self.fields['member'].queryset = Member.objects.filter(
            documentation_center=center, is_active=True
        )
        self.fields['books'].queryset = Book.objects.filter(
            documentation_center=center,
            status='available',
            is_digital=False,
            quantity_available__gt=0
        )
        # Apply Tailwind classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'address', 'role', 'date_hired', 'is_active'
        ]
        widgets = {
            'date_hired': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'})
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'E-mail',
            'phone_number': 'Téléphone',
            'address': 'Adresse',
            'role': 'Rôle',
            'date_hired': 'Date d\'embauche',
            'is_active': 'Actif'
        }

    def __init__(self, *args, **kwargs):
        # Remove 'center' from kwargs before calling parent's __init__
        kwargs.pop('center', None)
        super().__init__(*args, **kwargs)
        # Apply consistent Tailwind CSS classes
        for field_name, field in self.fields.items():
            if field_name != 'is_active':  # Skip for checkbox
                field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            
class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'description', 'start_date', 'end_date', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply consistent Tailwind CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm' 

class ArchiveForm(forms.ModelForm):
    class Meta:
        model = ArchivalDocument
        fields = ['title', 'description', 'file_upload', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Entrez une description du document...'}),
        }
        labels = {
            'title': 'Titre',
            'description': 'Description',
            'file_upload': 'Fichier',
            'status': 'Statut',
        }
        help_texts = {
            'title': 'Le titre du document',
            'description': 'Une description détaillée du contenu du document',
            'file_upload': 'Sélectionnez le fichier à archiver (PDF, DOCX, etc.)',
            'status': 'Définir la confidentialité du document',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply consistent Tailwind CSS classes and update choices
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            
        # Update status choices to French
        if 'status' in self.fields:
            self.fields['status'].choices = [
                ('public', 'Public'),
                ('confidential', 'Confidentiel')
            ]
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'

class TrainingSubjectForm(forms.ModelForm):
    class Meta:
        model = TrainingSubject
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': 'Nom du sujet',
            'description': 'Description',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'

class TrainingModuleForm(forms.ModelForm):
    class Meta:
        model = TrainingModule
        fields = [
            'title', 'subject', 'description', 'thumbnail', 
            'minimum_age_required', 'points_to_pass', 'status', 
            'duration_minutes', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        # Store the documentation center for validation
        self.documentation_center = kwargs.pop('documentation_center', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            return title
            
        # If we have a documentation center and this is a new module (no instance.pk)
        # or if we're changing the title of an existing module
        if self.documentation_center:
            # Check if a module with this title already exists in this center
            existing_modules = TrainingModule.objects.filter(
                documentation_center=self.documentation_center,
                title__iexact=title  # Case-insensitive comparison
            )
            
            # Exclude the current instance if we're editing
            if self.instance and self.instance.pk:
                existing_modules = existing_modules.exclude(pk=self.instance.pk)
                
            if existing_modules.exists():
                raise forms.ValidationError(
                    "Un module de formation avec ce titre existe déjà dans ce centre. "
                    "Veuillez choisir un titre différent."
                )
        return title

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'points', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm'

# Formset for the Answers of a single Question
AnswerFormSet = inlineformset_factory(
    Question,  # Parent model
    Answer,    # Child model
    fields=('answer_text', 'is_correct'),
    extra=1,   # Start with 2 empty answer fields
    can_delete=True
)

# Formset for the Questions of a single Lesson
QuestionFormSet = inlineformset_factory(
    Lesson,      # Parent model
    Question,    # Child model
    form=QuestionForm,
    extra=1,     # Start with 1 empty question field
    can_delete=True
)
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'lesson_type', 'video_url', 'text_content', 'order']
        widgets = {
            'text_content': forms.Textarea(attrs={'rows': 3, 'class': 'markdown-editor'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Add a specific class to toggle visibility based on lesson_type
            if field_name in ['video_url', 'text_content']:
                 field.widget.attrs['class'] = f'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm lesson-content-field'
            else:
                field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'


# A Formset is a collection of forms. This allows us to have multiple lesson forms on one page.
LessonFormSet = modelformset_factory(
    Lesson,
    form=LessonForm,
    extra=1, # Don't add empty lesson forms automatically
    can_delete=True, # Allow deleting lessons from the form
    fields=('title', 'lesson_type', 'video_url', 'text_content', 'order')
)

class CommuniqueForm(forms.ModelForm):
    class Meta:
        model = Communique
        fields = ['title', 'objective', 'message_body', 'target_activities']
        widgets = {
            'objective': forms.Textarea(attrs={'rows': 2}),
            'message_body': forms.Textarea(attrs={'rows': 8}),
            'target_activities': forms.SelectMultiple(attrs={'class': 'form-multiselect'}),
        }
        labels = {
            'title': 'Titre du Communiqué',
            'objective': 'Objectif',
            'message_body': 'Corps du Message',
            'target_activities': 'Cibler des Activités Spécifiques (Optionnel)',
        }
        help_texts = {
            'target_activities': "Laissez ce champ vide pour envoyer à tout le personnel.",
        }

    def __init__(self, center, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter the activities to show only those from the current center
        self.fields['target_activities'].queryset = Activity.objects.filter(
            documentation_center=center
        )
        # Apply Tailwind classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'biography', 'date_of_birth', 'date_of_death']
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'biography': 'Biographie',
            'date_of_birth': 'Date de naissance',
            'date_of_death': 'Date de décès',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'last_name': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'biography': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'rows': 4}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'date_of_death': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description']
        labels = {
            'name': 'Nom du Rôle',
            'description': 'Description du Rôle',
        }

class UserForm(forms.ModelForm):
    """Form for user account details (username, email, etc.)"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': _('Prénom'),
            'last_name': _('Nom'),
            'email': _('Adresse email'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind CSS classes
        for field in self.fields.values():
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'

class ProfileForm(forms.ModelForm):
    """Form for profile details (profile picture, phone, etc.)"""
    class Meta:
        model = Profile
        fields = ['profile_picture', 'establishment_name', 'phone_number', 'date_of_birth', 'bio']
        labels = {
            'profile_picture': _('Photo de profil'),
            'establishment_name': _("Nom de l'établissement"),
            'phone_number': _('Numéro de téléphone'),
            'date_of_birth': _('Date de naissance'),
            'bio': _('À propos de moi'),
        }
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind CSS classes
        for field in self.fields.values():
            if field.widget.__class__.__name__ != 'CheckboxInput':
                field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'


class DeletionJustificationForm(forms.Form):
    """
    Form for collecting deletion justification from users.
    """
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-textarea mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50',
            'rows': 4,
            'placeholder': 'Veuillez expliquer en détail la raison de cette suppression...',
            'required': True
        }),
        label='Justification de la suppression',
        help_text='Une explication détaillée est requise pour toute suppression.',
        required=True,
        min_length=10,
        max_length=1000
    )
    
    confirm_deletion = forms.BooleanField(
        label='Je confirme que je souhaite supprimer cet élément de façon permanente',
        required=True
    )


class ComplaintForm(forms.ModelForm):
    """
    Form for submitting complaints/help requests.
    """
    class Meta:
        model = Complaint
        fields = ['full_name', 'email', 'phone1', 'phone2', 'request']
        labels = {
            'full_name': 'Nom complet',
            'email': 'Email',
            'phone1': 'Téléphone 1',
            'phone2': 'Téléphone 2 (optionnel)',
            'request': 'Votre requête',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': 'Entrez votre nom complet'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': 'Entrez votre adresse email'
            }),
            'phone1': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': 'Entrez votre numéro de téléphone principal'
            }),
            'phone2': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': 'Entrez un numéro de téléphone secondaire (optionnel)'
            }),
            'request': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'rows': 5,
                'placeholder': 'Décrivez votre requête en détail...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required except phone2
        for field_name, field in self.fields.items():
            if field_name != 'phone2':
                field.required = True