# sydoc_project/center_panel/forms.py

from django import forms
from core.models import Book, Author, Category, Member, Loan, Staff

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