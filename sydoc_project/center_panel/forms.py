# sydoc_project/center_panel/forms.py

from django import forms
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib.auth.models import User
from core.models import LiteraryGenre, SubGenre, Theme, SousTheme
from django.utils.translation import gettext_lazy as _
from core.models import Book, BookVolume, Author, Member, Loan, Staff, Activity, ArchivalDocument, TrainingSubject, TrainingModule, Lesson, Question, Answer, Communique, Role, Profile, BookDigitization, DigitizedPage, Language, DeletedBook

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
            'title', 'isbn', 'publication_date', 'authors', 'description',
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
    """Enhanced loan form with age verification and volume selection"""
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
            'book', 'member', 'loan_date', 'due_date', 'volume',
            'member_age', 'age_verified', 'quantity'
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
            'volume': 'Tome/Volume',
            'member_age': 'Âge du membre',
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
        
        # Initially disable volume field until a book is selected
        self.fields['volume'].widget.attrs['disabled'] = 'disabled'
        self.fields['volume'].required = False
        
        # If we're editing an existing loan and it has a book with volumes
        if self.instance and self.instance.pk and self.instance.book and self.instance.book.has_volumes:
            self.fields['volume'].queryset = BookVolume.objects.filter(
                book=self.instance.book
            ).order_by('volume_number')
            self.fields['volume'].widget.attrs.pop('disabled', None)
            self.fields['volume'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        member = cleaned_data.get('member')
        member_age = cleaned_data.get('member_age')
        age_verified = cleaned_data.get('age_verified')
        volume = cleaned_data.get('volume')
        
        # Age verification checks
        if book and book.minimum_age_required > 0:
            if not age_verified:
                self.add_error('age_verified', "L'âge du membre doit être vérifié pour ce livre.")
            
            if not member_age:
                self.add_error('member_age', "L'âge du membre est requis pour ce livre.")
            elif member_age < book.minimum_age_required:
                self.add_error('member_age', f"Le membre doit avoir au moins {book.minimum_age_required} ans pour emprunter ce livre.")
        
        # Volume validation for multi-volume books
        if book and book.has_volumes and not volume:
            self.add_error('volume', "Veuillez sélectionner un tome/volume pour ce livre.")
        
        # Check if the book or volume is available
        quantity = cleaned_data.get('quantity', 1)
        if book and not book.has_volumes and book.quantity_available < quantity:
            self.add_error('quantity', f"Seulement {book.quantity_available} exemplaires disponibles pour ce livre.")
        elif book and book.has_volumes and volume and volume.quantity_available < quantity:
            self.add_error('quantity', f"Seulement {volume.quantity_available} exemplaires disponibles pour ce tome/volume.")
        
        return cleaned_data


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