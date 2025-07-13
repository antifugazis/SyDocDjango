# sydoc_project/center_panel/forms.py

from django import forms
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from core.models import Book, Author, Category, Member, Loan, Staff, Activity, ArchivalDocument, TrainingSubject, TrainingModule, Lesson, Question, Answer, Communique, Activity, Role, Profile

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        # Define the fields you want in the form
        fields = [
            'title', 'authors', 'category', 'isbn', 'publication_date',
            'description', 'quantity_available', 'total_quantity',
            'is_digital', 'file_upload', 'cover_image', 'status'
        ]
        # Use widgets to customize the form fields, e.g., for a date picker
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes to all form fields for consistent styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'address',
            'membership_type', 'is_active'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'membership_type': forms.Select(choices=Member.MEMBERSHIP_CHOICES),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'})
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'E-mail',
            'phone_number': 'Téléphone',
            'address': 'Adresse',
            'membership_type': 'Type d\'adhésion',
            'is_active': 'Actif',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply consistent Tailwind CSS classes
        for field_name, field in self.fields.items():
            if field_name != 'is_active':  # Skip checkbox as it has custom classes
                field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'

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

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {
            'name': 'Nom de la catégorie',
            'description': 'Description',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'description': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'rows': 3}),
        }

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