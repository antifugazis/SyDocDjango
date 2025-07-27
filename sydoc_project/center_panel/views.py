from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
import os
import io
import tempfile
import shutil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from PIL import Image, ImageEnhance
from core.models import DocumentationCenter, Book, Member, Loan, Staff, ArchivalDocument, TrainingModule, Activity, TrainingSubject, TrainingModule, Lesson, Communique, Question, Answer, StaffTrainingRecord, Quiz, Category, Author, Role, Profile, BookDigitization, DigitizedPage
from .forms import BookForm, MemberForm, CreateLoanForm, StaffForm, ActivityForm, ArchiveForm, TrainingSubjectForm, TrainingModuleForm, LessonFormSet, CommuniqueForm, TrainingModuleForm, LessonForm, QuestionFormSet, CategoryForm, AuthorForm, RoleForm, UserForm, ProfileForm
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

# Helper to check if a user is associated with a DocumentationCenter (placeholder for now)
# In a real app, you'd link Django User to DocumentationCenter,
# or ensure a custom user model is used. For now, we'll assume a direct link,
# or that a logged-in user is implicitly managing *a* center for development.

# TODO: Implement robust way to link logged-in User to their DocumentationCenter
# For now, we'll pick a center for demonstration.
# In a real setup, User would have a ForeignKey to DocumentationCenter or vice-versa.
# For example: request.user.documentation_center (if User model had this field)

@login_required # Requires the user to be logged in
def center_dashboard(request):
    # Placeholder: In a real application, you'd get the center associated with the logged-in user
    # For development, let's just pick the first center or ensure one exists
    try:
        # Assuming for now, the user directly relates to a center
        # Or, for testing, grab the first one:
        current_center = DocumentationCenter.objects.first()
        if not current_center:
            messages.error(request, "Aucun centre de documentation trouvé. Veuillez en créer un via l'administration Superadmin.")
            return redirect('admin:index') # Redirect to admin if no center exists

    except DocumentationCenter.DoesNotExist:
        messages.error(request, "Votre compte n'est associé à aucun centre de documentation.")
        return redirect('login') # Or wherever your login page is

    # --- Dashboard Statistics for the current_center ---
    stats_data = {
        'total_books': Book.objects.filter(documentation_center=current_center).count(),
        'physical_books': Book.objects.filter(documentation_center=current_center, is_digital=False).count(),
        'ebooks': Book.objects.filter(documentation_center=current_center, is_digital=True).count(),
        'total_members': Member.objects.filter(documentation_center=current_center).count(),
        'active_loans': Loan.objects.filter(book__documentation_center=current_center, status__in=['borrowed', 'overdue']).count(),
        'overdue_loans': Loan.objects.filter(book__documentation_center=current_center, status='overdue').count(),
        'total_staff': Staff.objects.filter(documentation_center=current_center).count(),
        'total_archives': ArchivalDocument.objects.filter(documentation_center=current_center).count(),
        'total_training_modules': TrainingModule.objects.filter(documentation_center=current_center).count(),
        
        # New statistics for the dashboard
        'total_book_cost': Book.objects.filter(documentation_center=current_center).exclude(price__isnull=True).aggregate(Sum('price'))['price__sum'] or 0,
        'total_activities': Activity.objects.filter(documentation_center=current_center).count(),
        'total_roles': Role.objects.count(),  # Removed documentation_center filter as Role is not center-specific
        'digitized_books': BookDigitization.objects.filter(book__documentation_center=current_center).count(),
        'digitization_progress': round((BookDigitization.objects.filter(book__documentation_center=current_center).count() / 
                                    max(Book.objects.filter(documentation_center=current_center, is_digital=False).count(), 1)) * 100, 1),
        'active_users': User.objects.filter(last_login__gte=timezone.now() - timedelta(days=1)).count(),
    }
    
    # Recent Loans (last 5)
    recent_loans = Loan.objects.filter(
        book__documentation_center=current_center
    ).order_by('-loan_date')[:5]
    
    # Add is_overdue flag to each loan


    
    # Upcoming Returns (next 5 due)
    upcoming_returns = Loan.objects.filter(
        book__documentation_center=current_center,
        status__in=['borrowed', 'overdue'],
        return_date__isnull=True
    ).order_by('due_date')[:5]
    
    # Add days_left to each upcoming return
    for loan in upcoming_returns:
        loan.days_left = (loan.due_date - timezone.localdate()).days
        loan.days_left_abs = abs(loan.days_left)
    
    context = {
        'current_center': current_center,
        'stats': stats_data,
        'recent_loans': recent_loans,
        'upcoming_returns': upcoming_returns,
        'current_date': timezone.localdate(),
    }
    return render(request, 'center_panel/dashboard.html', context)


@login_required
def center_book_list(request):
    # Placeholder: Similar to dashboard, link to the actual center
    try:
        current_center = DocumentationCenter.objects.first() # For dev purposes
        if not current_center:
            messages.error(request, "Aucun centre de documentation trouvé pour l'utilisateur actuel.")
            return redirect('admin:index')

    except DocumentationCenter.DoesNotExist:
        messages.error(request, "Votre compte n'est associé à aucun centre de documentation.")
        return redirect('login')

    books = Book.objects.filter(documentation_center=current_center).order_by('title')

    context = {
        'current_center': current_center,
        'books': books
    }
    return render(request, 'center_panel/books.html', context)


@login_required
def book_detail(request, pk):
    """View for displaying details of a specific book."""
    current_center = DocumentationCenter.objects.first()
    if not current_center:
        messages.error(request, "Aucun centre de documentation trouvé.")
        return redirect('admin:index')
    
    book = get_object_or_404(Book, pk=pk, documentation_center=current_center)
    
    context = {
        'book': book,
        'current_center': current_center
    }
    return render(request, 'center_panel/book_detail.html', context)

@login_required
def add_book(request):
    current_center = DocumentationCenter.objects.first()
    if request.method == 'POST':
        # Pass the form data and any uploaded files
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.documentation_center = current_center
            book.save()
            form.save_m2m() # Needed to save ManyToMany relationships like 'authors'
            messages.success(request, f"Le livre '{book.title}' a été ajouté avec succès.")
            return redirect('center_panel:books')
    else:
        form = BookForm()
        
    context = {
        'form': form,
        'current_center': current_center
    }
    return render(request, 'center_panel/admin/add_edit_book.html', context)

@login_required
def edit_book(request, pk):
    current_center = DocumentationCenter.objects.first()
    book = get_object_or_404(Book, pk=pk, documentation_center=current_center)
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le livre '{book.title}' a été mis à jour.")
            return redirect('center_panel:books')
    else:
        form = BookForm(instance=book)

    context = {
        'form': form,
        'book': book, # Pass the book instance to the template
        'current_center': current_center
    }
    # We can reuse the same template for both adding and editing
    return render(request, 'center_panel/admin/add_edit_book.html', context)


@login_required
def delete_book(request, pk):
    current_center = DocumentationCenter.objects.first()
    book = get_object_or_404(Book, pk=pk, documentation_center=current_center)
    
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f"Le livre '{book_title}' a été supprimé.")
        return redirect('center_panel:books')
        
    context = {
        'book': book,
        'current_center': current_center
    }
    return render(request, 'center_panel/admin/delete_book_confirm.html', context)

@login_required
def member_list(request):
    current_center = DocumentationCenter.objects.first()
    members = Member.objects.filter(documentation_center=current_center).order_by('last_name', 'first_name')
    
    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        members = members.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    context = {
        'current_center': current_center,
        'members': members,
        'search_query': search_query
    }
    return render(request, 'center_panel/members.html', context)

@login_required
def add_member(request):
    current_center = DocumentationCenter.objects.first()
    
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.documentation_center = current_center
            member.save()
            
            # Generate member ID if not provided
            if not member.member_id:
                member.member_id = f"MEM-{member.id:04d}"
                member.save(update_fields=['member_id'])
            
            messages.success(
                request, 
                f"Le membre {member.first_name} {member.last_name} a été ajouté avec succès."
            )
            return redirect('center_panel:members')
    else:
        form = MemberForm()

    context = {
        'form': form,
        'current_center': current_center,
        'title': 'Ajouter un nouveau membre',
    }
    return render(request, 'center_panel/admin/add_edit_member.html', context)

@login_required
def edit_member(request, pk):
    current_center = DocumentationCenter.objects.first()
    member = get_object_or_404(Member, pk=pk, documentation_center=current_center)
    
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(
                request, 
                f"Les informations de {member.first_name} {member.last_name} ont été mises à jour."
            )
            return redirect('center_panel:members')
    else:
        form = MemberForm(instance=member)

    context = {
        'form': form,
        'member': member,
        'current_center': current_center,
        'title': f"Modifier {member.first_name} {member.last_name}",
    }
    return render(request, 'center_panel/admin/add_edit_member.html', context)

@login_required
def delete_member(request, pk):
    current_center = DocumentationCenter.objects.first()
    member = get_object_or_404(Member, pk=pk, documentation_center=current_center)
    
    if request.method == 'POST':
        member_name = f"{member.first_name} {member.last_name}"
        member.delete()
        messages.success(request, f"Le membre '{member_name}' a été supprimé.")
        return redirect('center_panel:members')

    context = {
        'member': member,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/delete_member_confirm.html', context)

@login_required
def loan_list(request):
    # Get the current center
    current_center = DocumentationCenter.objects.first()
    if not current_center:
        messages.error(request, "Aucun centre de documentation trouvé.")
        return redirect('admin:index')
        
    # Get base queryset
    loans = Loan.objects.filter(book__documentation_center=current_center)
    
    # Apply search filter if provided
    search_query = request.GET.get('search', '')
    if search_query:
        loans = loans.filter(
            Q(book__title__icontains=search_query) |
            Q(book__isbn__icontains=search_query) |
            Q(member__first_name__icontains=search_query) |
            Q(member__last_name__icontains=search_query) |
            Q(member__member_id__icontains=search_query)
        )
    
    # Apply status filter if provided
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        loans = loans.filter(return_date__isnull=True)
    elif status_filter == 'overdue':
        loans = loans.filter(return_date__isnull=True, due_date__lt=timezone.now().date())
    elif status_filter == 'returned':
        loans = loans.filter(return_date__isnull=False)
    
    # Order by due date (overdue first, then by due date, then by loan date)
    loans = loans.order_by(
        'return_date',  # Returned loans last
        'due_date',     # Then by due date
        '-loan_date'    # Most recent loans first
    )
    
    # Counts for status filters
    total_loans = loans.count()
    active_loans = loans.filter(return_date__isnull=True).count()
    overdue_loans = loans.filter(return_date__isnull=True, due_date__lt=timezone.now().date()).count()
    returned_loans = loans.filter(return_date__isnull=False).count()
    
    context = {
        'current_center': current_center,
        'loans': loans,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_loans': total_loans,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
        'returned_loans': returned_loans,
    }
    return render(request, 'center_panel/loans.html', context)
@login_required
def add_loan(request):
    current_center = DocumentationCenter.objects.first()
    if request.method == 'POST':
        form = CreateLoanForm(center=current_center, data=request.POST)
        if form.is_valid():
            member = form.cleaned_data['member']
            books_to_loan = form.cleaned_data['books']
            due_date = form.cleaned_data['due_date']
            
            try:
                # Create a loan for each selected book
                for book in books_to_loan:
                    # Create the loan
                    Loan.objects.create(
                        book=book,
                        member=member,
                        due_date=due_date,
                        status='borrowed',
                        loan_date=timezone.now().date()
                    )
                    
                    # Decrease the book's available quantity
                    book.quantity_available = max(0, book.quantity_available - 1)
                    book.save()
                
                messages.success(
                    request, 
                    f"Les prêts pour {member.first_name} {member.last_name} ont été enregistrés avec succès."
                )
                return redirect('center_panel:loans')
                
            except Exception as e:
                messages.error(
                    request, 
                    f"Une erreur s'est produite lors de l'enregistrement du prêt : {str(e)}"
                )
    else:
        form = CreateLoanForm(center=current_center)

    context = {
        'form': form,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/add_loan.html', context)

@login_required
def return_loan(request, loan_id):
    """
    Mark a loan as returned and update the book's availability.
    """
    current_center = DocumentationCenter.objects.first()
    loan = get_object_or_404(Loan, 
                           id=loan_id, 
                           book__documentation_center=current_center,
                           return_date__isnull=True)  # Only process if not already returned
    
    if request.method == 'POST':
        loan.return_date = timezone.now().date()
        loan.status = 'returned'
        loan.save()
        
        # Update book availability
        book = loan.book
        book.quantity_available += 1
        book.save()
        
        messages.success(request, f"Le livre '{loan.book.title}' a été marqué comme retourné.")
        return redirect('center_panel:loans')
    
    # If not a POST request, redirect to loans list
    return redirect('center_panel:loans')
@login_required
def staff_list(request):
    # Get the current center
    current_center = DocumentationCenter.objects.first()
    if not current_center:
        messages.error(request, "Aucun centre de documentation trouvé.")
        return redirect('admin:index')
        
    # Get staff for this center
    staff = Staff.objects.filter(documentation_center=current_center)
    
    context = {
        'current_center': current_center,
        'staff': staff
    }
    return render(request, 'center_panel/staff.html', context)

@login_required
def add_staff(request):
    current_center = DocumentationCenter.objects.first()
    if request.method == 'POST':
        form = StaffForm(data=request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.documentation_center = current_center
            staff.save()
            messages.success(request, f"Le membre du personnel '{staff.full_name}' a été ajouté.")
            return redirect('center_panel:staff')
    else:
        form = StaffForm()

    context = {
        'form': form,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/add_edit_staff.html', context)

@login_required
def edit_staff(request, pk):
    current_center = DocumentationCenter.objects.first()
    staff = get_object_or_404(Staff, pk=pk, documentation_center=current_center)
    
    if request.method == 'POST':
        form = StaffForm(data=request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, f"Les informations de '{staff.full_name}' ont été mises à jour.")
            return redirect('center_panel:staff')
    else:
        form = StaffForm(instance=staff)

    context = {
        'form': form,
        'staff': staff,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/add_edit_staff.html', context)

@login_required
def delete_staff(request, pk):
    current_center = DocumentationCenter.objects.first()
    staff = get_object_or_404(Staff, pk=pk, documentation_center=current_center)
    
    if request.method == 'POST':
        staff_name = staff.full_name
        staff.delete()
        messages.success(request, f"Le membre du personnel '{staff_name}' a été supprimé.")
        return redirect('center_panel:staff')

    context = {
        'staff': staff,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/delete_staff_confirm.html', context)

@login_required
def archive_list(request):
    # Get the current center
    current_center = DocumentationCenter.objects.first()
    if not current_center:
        messages.error(request, "Aucun centre de documentation trouvé.")
        return redirect('admin:index')
        
    # Get archives for this center
    archives = ArchivalDocument.objects.filter(documentation_center=current_center)
    
    context = {
        'current_center': current_center,
        'archives': archives
    }
    return render(request, 'center_panel/archives.html', context)

@login_required
def training_list(request):
    # Get the current center
    current_center = DocumentationCenter.objects.first()
    if not current_center:
        messages.error(request, "Aucun centre de documentation trouvé.")
        return redirect('admin:index')
        
    # Get training modules for this center
    trainings = TrainingModule.objects.filter(documentation_center=current_center)
    
    context = {
        'current_center': current_center,
        'trainings': trainings
    }
    return render(request, 'center_panel/trainings.html', context)

@login_required
def notification_list(request):
    # Get the current center
    current_center = DocumentationCenter.objects.first()
    if not current_center:
        messages.error(request, "Aucun centre de documentation trouvé.")
        return redirect('admin:index')
        
    context = {
        'current_center': current_center,
        'notifications': [] # Placeholder for notifications
    }
    return render(request, 'center_panel/notifications.html', context)

@login_required
def activity_list(request):
    current_center = DocumentationCenter.objects.first()
    activities = Activity.objects.filter(documentation_center=current_center)
    context = {
        'current_center': current_center,
        'activities': activities
    }
    return render(request, 'center_panel/activities.html', context)

@login_required
def add_activity(request):
    current_center = DocumentationCenter.objects.first()
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            # Check if this is a duplicate submission (e.g., from browser refresh)
            if request.session.get('activity_form_submitted'):
                # Clear the session flag and redirect to prevent duplicate
                request.session['activity_form_submitted'] = False
                return redirect('center_panel:activities')
            
            # Set session flag to prevent duplicate submissions
            request.session['activity_form_submitted'] = True
            
            activity = form.save(commit=False)
            activity.documentation_center = current_center
            activity.save()
            messages.success(request, "L'activité a été créée avec succès.")
            return redirect('center_panel:activities')
    else:
        form = ActivityForm()

    context = {
        'form': form,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/add_edit_activity.html', context)

@login_required
def edit_activity(request, pk):
    current_center = DocumentationCenter.objects.first()
    activity = get_object_or_404(Activity, pk=pk, documentation_center=current_center)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, "L'activité a été mise à jour.")
            return redirect('center_panel:activities')
    else:
        form = ActivityForm(instance=activity)

    context = {
        'form': form,
        'activity': activity,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/add_edit_activity.html', context)

@login_required
def delete_activity(request, pk):
    current_center = DocumentationCenter.objects.first()
    activity = get_object_or_404(Activity, pk=pk, documentation_center=current_center)

    if request.method == 'POST':
        # Check if this is a duplicate submission
        if request.session.get('activity_delete_submitted'):
            # Clear the session flag and redirect to prevent duplicate
            request.session['activity_delete_submitted'] = False
            return redirect('center_panel:activities')
        
        # Set session flag to prevent duplicate submissions
        request.session['activity_delete_submitted'] = True
        
        activity_name = activity.name
        activity.delete()
        messages.success(request, f"L'activité '{activity_name}' a été supprimée.")
        return redirect('center_panel:activities')

    context = {
        'activity': activity,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/delete_activity_confirm.html', context)

@login_required
def archive_list(request):
    current_center = DocumentationCenter.objects.first()
    archives = ArchivalDocument.objects.filter(documentation_center=current_center)
    context = {
        'current_center': current_center,
        'archives': archives
    }
    return render(request, 'center_panel/archives.html', context)

@login_required
def add_archive(request):
    current_center = DocumentationCenter.objects.first()
    if request.method == 'POST':
        form = ArchiveForm(request.POST, request.FILES)
        if form.is_valid():
            archive = form.save(commit=False)
            archive.documentation_center = current_center
            archive.save()
            messages.success(request, "Le document d'archive a été ajouté avec succès.")
            return redirect('center_panel:archives')
    else:
        form = ArchiveForm()

    context = {
        'form': form,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/add_edit_archive.html', context)

@login_required
def edit_archive(request, pk):
    current_center = DocumentationCenter.objects.first()
    archive = get_object_or_404(ArchivalDocument, pk=pk, documentation_center=current_center)
    if request.method == 'POST':
        form = ArchiveForm(request.POST, request.FILES, instance=archive)
        if form.is_valid():
            form.save()
            messages.success(request, "Le document d'archive a été mis à jour.")
            return redirect('center_panel:archives')
    else:
        form = ArchiveForm(instance=archive)

    context = {
        'form': form,
        'archive': archive,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/add_edit_archive.html', context)

@login_required
def download_archive(request, pk):
    """
    View to handle secure file downloads for archival documents.
    """
    current_center = DocumentationCenter.objects.first()
    archive = get_object_or_404(ArchivalDocument, pk=pk, documentation_center=current_center)
    
    if not archive.file_upload:
        messages.error(request, "Aucun fichier n'est associé à ce document d'archive.")
        return redirect('center_panel:archives')
    
    file_path = archive.file_upload.path
    
    if not os.path.exists(file_path):
        messages.error(request, "Le fichier demandé n'existe plus sur le serveur.")
        return redirect('center_panel:archives')
    
    # Get the file name from the path
    file_name = os.path.basename(file_path)
    
    # Open the file in binary mode for reading
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

@login_required
def delete_archive(request, pk):
    current_center = DocumentationCenter.objects.first()
    archive = get_object_or_404(ArchivalDocument, pk=pk, documentation_center=current_center)

    if request.method == 'POST':
        archive_name = archive.title
        archive.delete()
        messages.success(request, f"Le document d'archive '{archive_name}' a été supprimé avec succès.")
        return redirect('center_panel:archives')
        
    context = {
        'archive': archive,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/delete_archive_confirm.html', context)

@login_required
def training_subject_list(request):
    subjects = TrainingSubject.objects.all()
    context = {
        'current_center': DocumentationCenter.objects.first(),
        'subjects': subjects
    }
    return render(request, 'center_panel/training_subjects.html', context)

@login_required
def add_training_subject(request):
    if request.method == 'POST':
        form = TrainingSubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Le sujet de formation a été créé avec succès.")
            return redirect('center_panel:training_subjects')
    else:
        form = TrainingSubjectForm()

    context = {
        'form': form,
        'current_center': DocumentationCenter.objects.first(),
    }
    return render(request, 'center_panel/admin/add_edit_training_subject.html', context)

@login_required
def edit_training_subject(request, pk):
    subject = get_object_or_404(TrainingSubject, pk=pk)
    if request.method == 'POST':
        form = TrainingSubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, "Le sujet de formation a été mis à jour.")
            return redirect('center_panel:training_subjects')
    else:
        form = TrainingSubjectForm(instance=subject)

    context = {
        'form': form,
        'subject': subject,
        'current_center': DocumentationCenter.objects.first(),
    }
    return render(request, 'center_panel/admin/add_edit_training_subject.html', context)

@login_required
def delete_training_subject(request, pk):
    subject = get_object_or_404(TrainingSubject, pk=pk)
    # Optional: Check if subject is in use before deleting
    if subject.modules.exists():
        messages.error(request, f"Impossible de supprimer le sujet '{subject.name}' car il est utilisé par une ou plusieurs formations.")
        return redirect('center_panel:training_subjects')

    if request.method == 'POST':
        subject_name = subject.name
        subject.delete()
        messages.success(request, f"Le sujet '{subject_name}' a été supprimé.")
        return redirect('center_panel:training_subjects')

    context = {
        'subject': subject,
        'current_center': DocumentationCenter.objects.first(),
    }
    return render(request, 'center_panel/admin/delete_training_subject_confirm.html', context)

@login_required
def add_training_module(request):
    current_center = DocumentationCenter.objects.first()
    
    if request.method == 'POST':
        # Process the main form and the formset
        form = TrainingModuleForm(request.POST, request.FILES, documentation_center=current_center)
        lesson_formset = LessonFormSet(request.POST, queryset=Lesson.objects.none())

        if form.is_valid() and lesson_formset.is_valid():
            # First, save the main training module
            training_module = form.save(commit=False)
            training_module.documentation_center = current_center
            training_module.save()

            # Now, save the lessons associated with this module
            lessons = lesson_formset.save(commit=False)
            for lesson in lessons:
                lesson.training_module = training_module
                lesson.save()
            
            # Handle deleted lessons if any
            lesson_formset.save_m2m()

            messages.success(request, f"La formation '{training_module.title}' a été créée avec succès.")
            return redirect('center_panel:trainings') # Redirect to a list view we'll create later
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
            
    else:
        # On a GET request, show an empty form and formset
        form = TrainingModuleForm(documentation_center=current_center)
        lesson_formset = LessonFormSet(queryset=Lesson.objects.none())

    context = {
        'form': form,
        'lesson_formset': lesson_formset,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/add_edit_training_module.html', context)


@login_required
def training_list(request):
    """
    This view replaces the placeholder and lists all training modules.
    """
    current_center = DocumentationCenter.objects.first()
    trainings = TrainingModule.objects.filter(documentation_center=current_center)
    
    context = {
        'trainings': trainings,
        'current_center': current_center
    }
    return render(request, 'center_panel/trainings.html', context)

@login_required
def training_detail(request, pk):
    """
    Display the details of a specific training module.
    """
    current_center = DocumentationCenter.objects.first()
    training = get_object_or_404(TrainingModule, pk=pk, documentation_center=current_center)
    
    context = {
        'training': training,
        'current_center': current_center,
    }
    return render(request, 'center_panel/training_detail.html', context)

@login_required
def lesson_detail(request, pk):
    """
    Display the details of a specific lesson.
    """
    lesson = get_object_or_404(Lesson, pk=pk)
    current_center = DocumentationCenter.objects.first()
    
    # Ensure the lesson belongs to a training module in the current center
    if lesson.training_module.documentation_center != current_center:
        messages.error(request, "Vous n'avez pas accès à cette leçon.")
        return redirect('center_panel:trainings')
    
    context = {
        'lesson': lesson,
        'current_center': current_center,
    }
    return render(request, 'center_panel/lesson_detail.html', context)

@login_required
def lesson_list(request):
    """View to display all lessons grouped by their training modules"""
    # Get all training modules with their lessons
    trainings = TrainingModule.objects.prefetch_related('lessons').all()
    
    # Filter access based on user permissions
    if not request.user.is_staff:
        trainings = trainings.filter(status='published')
    
    context = {
        'trainings': trainings,
    }
    
    return render(request, 'center_panel/lesson_list.html', context)

@login_required
def lesson_quiz(request, pk):
    """
    Display the quiz for a specific lesson.
    This is a placeholder view that will be implemented later.
    """
    lesson = get_object_or_404(Lesson, pk=pk)
    current_center = DocumentationCenter.objects.first()
    
    # Ensure the lesson belongs to a training module in the current center
    if lesson.training_module.documentation_center != current_center:
        messages.error(request, "Vous n'avez pas accès à ce quiz.")
        return redirect('center_panel:trainings')
    
    # This is a placeholder - you'll implement the actual quiz functionality later
    context = {
        'lesson': lesson,
        'current_center': current_center,
    }
    return render(request, 'center_panel/lesson_quiz.html', context)



@login_required
def edit_training_module(request, pk):
    current_center = DocumentationCenter.objects.first()
    training_module = get_object_or_404(TrainingModule, pk=pk, documentation_center=current_center)

    if request.method == 'POST':
        form = TrainingModuleForm(request.POST, request.FILES, instance=training_module)
        if form.is_valid():
            # Save the main module first
            module = form.save()
            
            # Now process the lessons and their nested questions
            lessons = module.lessons.all()
            for lesson in lessons:
                # Create a QuestionFormSet for each individual lesson
                question_formset = QuestionFormSet(request.POST, instance=lesson, prefix=f'questions-{lesson.id}')
                if question_formset.is_valid():
                    question_formset.save()

            messages.success(request, f"La formation '{module.title}' et ses quiz ont été mis à jour.")
            return redirect('center_panel:trainings')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")

    else: # GET request
        form = TrainingModuleForm(instance=training_module)

    # Prepare a list of formsets, one for each lesson, for the template
    lesson_question_formsets = []
    for lesson in training_module.lessons.all():
        lesson_question_formsets.append({
            'lesson': lesson,
            'formset': QuestionFormSet(instance=lesson, prefix=f'questions-{lesson.id}')
        })

    context = {
        'form': form,
        'training_module': training_module,
        'lesson_question_formsets': lesson_question_formsets, # Pass the list of formsets
        'current_center': current_center,
    }
    # We reuse the same template for adding and editing
    return render(request, 'center_panel/admin/add_edit_training_module.html', context)


@login_required
def delete_training_module(request, pk):
    current_center = DocumentationCenter.objects.first()
    training_module = get_object_or_404(TrainingModule, pk=pk, documentation_center=current_center)

    if request.method == 'POST':
        module_title = training_module.title
        training_module.delete()
        messages.success(request, f"La formation '{module_title}' et toutes ses leçons ont été supprimées.")
        return redirect('center_panel:trainings')

    context = {
        'training': training_module,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/delete_training_confirm.html', context)

@login_required
def communique_list(request):
    current_center = DocumentationCenter.objects.first()
    communiques = Communique.objects.filter(documentation_center=current_center)
    context = {
        'current_center': current_center,
        'communiques': communiques,
    }
    return render(request, 'center_panel/communiques.html', context)

@login_required
def add_communique(request):
    current_center = DocumentationCenter.objects.first()
    if request.method == 'POST':
        form = CommuniqueForm(center=current_center, data=request.POST)
        if form.is_valid():
            communique = form.save(commit=False)
            communique.documentation_center = current_center
            # Assuming the logged-in user is a Staff member
            # In a real app, you'd get this from the request.user
            communique.author = Staff.objects.first() # Placeholder
            communique.save()
            form.save_m2m() # Save ManyToMany relationships
            messages.success(request, "Le communiqué a été publié avec succès.")
            return redirect('center_panel:communiques')
    else:
        form = CommuniqueForm(center=current_center)

    context = {
        'form': form,
        'current_center': current_center,
    }
    return render(request, 'center_panel/add_edit_communique.html', context)

@login_required
def communique_detail(request, pk):
    current_center = DocumentationCenter.objects.first()
    communique = get_object_or_404(Communique, pk=pk, documentation_center=current_center)
    context = {
        'current_center': current_center,
        'communique': communique,
    }
    return render(request, 'center_panel/communique_detail.html', context)

@login_required
def lesson_quiz(request, pk):
    """
    Displays the quiz for a specific lesson and processes the submission.
    """
    print("\n=== DEBUG: lesson_quiz view started ===")
    print(f"Request method: {request.method}")
    print(f"Lesson PK: {pk}")
    
    # Get current center (using first() for now, should be from request.user in production)
    current_center = DocumentationCenter.objects.first()
    print(f"Current center: {current_center}")
    
    # Debug: Print all lessons to check if the requested one exists
    all_lessons = Lesson.objects.all()
    print(f"\nAll lessons in database ({all_lessons.count()} total):")
    for l in all_lessons:
        print(f"- {l.id}: {l.title} (Module: {l.training_module.title} - Center: {l.training_module.documentation_center.name if l.training_module.documentation_center else 'None'})")
    
    # Get the requested lesson
    try:
        lesson = Lesson.objects.get(
            pk=pk,
            training_module__documentation_center=current_center
        )
        print(f"\nFound lesson: {lesson.title} (ID: {lesson.id})")
    except Lesson.DoesNotExist:
        print(f"\nERROR: Lesson with pk={pk} not found for center {current_center}")
        raise Http404("Lesson not found")
    
    # Get all questions for the lesson
    questions = lesson.questions.prefetch_related('answers').all()
    questions_count = questions.count()
    print(f"\nFound {questions_count} questions for lesson {lesson.id}:")
    
    # Debug: Print detailed question and answer information
    for i, question in enumerate(questions, 1):
        answers = list(question.answers.all())
        print(f"\nQuestion {i} (ID: {question.id}, Points: {question.points}): {question.question_text}")
        print(f"  Answers ({len(answers)}):")
        for j, answer in enumerate(answers, 1):
            print(f"  {j}. {answer.answer_text} (ID: {answer.id}, Correct: {answer.is_correct})")
    
    # This is a placeholder for the current staff member taking the quiz
    # In a real app, you would get this from the logged-in user's profile
    current_staff_member = Staff.objects.first() 

    if request.method == 'POST':
        total_possible_points = questions.aggregate(total=Sum('points'))['total'] or 0
        user_score = 0
        
        # Loop through each question to check the submitted answer
        for question in questions:
            submitted_answer_id = request.POST.get(f'question_{question.id}')
            if submitted_answer_id:
                try:
                    # Check if the submitted answer is correct
                    correct_answer = question.answers.get(id=submitted_answer_id, is_correct=True)
                    user_score += question.points
                except Answer.DoesNotExist:
                    # The submitted answer was incorrect
                    pass
        
        # Calculate the final percentage
        final_percentage = (user_score / total_possible_points * 100) if total_possible_points > 0 else 0

        # Create or update the training record
        training_record, created = StaffTrainingRecord.objects.update_or_create(
            staff_member=current_staff_member,
            training_module=lesson.training_module,
            defaults={
                'score': final_percentage,
                'passed': final_percentage >= lesson.training_module.points_to_pass,
                'completion_date': timezone.now().date()
            }
        )

        # Redirect to a new results page
        return redirect('center_panel:quiz_results', pk=training_record.pk)

    context = {
        'lesson': lesson,
        'questions': questions,
        'current_center': current_center,
    }
    # Use the SurveyJS template instead of the direct rendering template
    return render(request, 'center_panel/lesson_quiz.html', context)


# --- ADD THIS NEW view for the results page ---

@login_required
def quiz_results(request, pk):
    """
    Displays the results of a completed quiz to the user.
    """
    current_center = DocumentationCenter.objects.first()
    # Get the specific training record to show the results
    training_record = get_object_or_404(
        StaffTrainingRecord,
        pk=pk,
        training_module__documentation_center=current_center
    )
    
    context = {
        'training_record': training_record,
        'current_center': current_center,
    }
    return render(request, 'center_panel/public/quiz_results_page.html', context)

@login_required
def lesson_quiz_api(request, pk):
    """
    This view provides the quiz data in a JSON format for the SurveyJS library.
    """
    lesson = get_object_or_404(Lesson, pk=pk)
    questions = lesson.questions.prefetch_related('answers')

    # Build the JSON structure that SurveyJS expects
    survey_json = {
        "title": f"Quiz for {lesson.title}",
        "showQuestionNumbers": "on",
        "completedHtml": "<h4>You have answered correctly <b>{correctAnswers}</b> out of <b>{questionCount}</b> questions.</h4>", # Results page
        "pages": [
            {
                "name": "quiz_page",
                "elements": [
                    {
                        "type": "radiogroup", # for multiple choice
                        "name": str(q.id),
                        "title": q.question_text,
                        "choices": [
                            {
                                "value": str(a.id),
                                "text": a.answer_text
                            } for a in q.answers.all()
                        ],
                        "correctAnswer": str(q.answers.get(is_correct=True).id) if q.answers.filter(is_correct=True).exists() else None
                    } for q in questions if q.question_type == 'mc'
                ]
            }
        ]
    }
    
    return JsonResponse(survey_json)

# Category CRUD Views
@login_required
def category_list(request):
    """Display all book categories."""
    current_center = DocumentationCenter.objects.first()
    categories = Category.objects.all().order_by('name')
    
    context = {
        'categories': categories,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/category_list.html', context)

@login_required
def add_category(request):
    """Add a new book category."""
    current_center = DocumentationCenter.objects.first()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Catégorie ajoutée avec succès.')
            return redirect('center_panel:categories')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'current_center': current_center,
        'is_add': True,
    }
    return render(request, 'center_panel/admin/add_edit_category.html', context)

@login_required
def edit_category(request, pk):
    """Edit an existing book category."""
    current_center = DocumentationCenter.objects.first()
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Catégorie modifiée avec succès.')
            return redirect('center_panel:categories')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'current_center': current_center,
        'is_add': False,
    }
    return render(request, 'center_panel/admin/add_edit_category.html', context)

@login_required
def delete_category(request, pk):
    """Delete a book category."""
    category = get_object_or_404(Category, pk=pk)
    
    # Check if the category is associated with any books
    if Book.objects.filter(category=category).exists():
        messages.error(request, 'Impossible de supprimer cette catégorie car elle est associée à des livres.')
    else:
        category.delete()
        messages.success(request, 'Catégorie supprimée avec succès.')
    
    return redirect('center_panel:categories')

# Author CRUD Views
@login_required
def author_list(request):
    """Display all book authors."""
    current_center = DocumentationCenter.objects.first()
    authors = Author.objects.all().order_by('last_name', 'first_name')
    
    context = {
        'authors': authors,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/author_list.html', context)

@login_required
def add_author(request):
    """Add a new book author."""
    current_center = DocumentationCenter.objects.first()
    
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Auteur ajouté avec succès.')
            return redirect('center_panel:authors')
    else:
        form = AuthorForm()
    
    context = {
        'form': form,
        'current_center': current_center,
        'is_add': True,
    }
    return render(request, 'center_panel/admin/add_edit_author.html', context)

@login_required
def edit_author(request, pk):
    """Edit an existing book author."""
    current_center = DocumentationCenter.objects.first()
    author = get_object_or_404(Author, pk=pk)
    
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            messages.success(request, 'Auteur modifié avec succès.')
            return redirect('center_panel:authors')
    else:
        form = AuthorForm(instance=author)
    
    context = {
        'form': form,
        'author': author,
        'current_center': current_center,
        'is_add': False,
    }
    return render(request, 'center_panel/admin/add_edit_author.html', context)

@login_required
def delete_author(request, pk):
    """Delete a book author."""
    author = get_object_or_404(Author, pk=pk)
    
    # Check if the author is associated with any books
    if author.book_set.exists():
        messages.error(request, 'Impossible de supprimer cet auteur car il est associé à des livres.')
    else:
        author.delete()
        messages.success(request, 'Auteur supprimé avec succès.')
    
    return redirect('center_panel:authors')

# Profile Management Views
def profile_list(request):
    """
    List all user profiles with their associated information.
    """
    profiles = Profile.objects.select_related('user').all()
    context = {
        'profiles': profiles,
        'title': 'Gestion des profils utilisateurs'
    }
    return render(request, 'center_panel/profiles/profile_list.html', context)

def profile_detail(request, pk):
    """
    Display detailed information about a specific user profile.
    """
    profile = get_object_or_404(Profile, pk=pk)
    context = {
        'profile': profile,
        'title': f'Profil de {profile.user.get_full_name() or profile.user.username}'
    }
    return render(request, 'center_panel/profiles/profile_detail.html', context)

@login_required
def edit_profile(request, pk):
    """
    Edit an existing user profile.
    """
    profile = get_object_or_404(Profile, pk=pk)
    user = profile.user
    
    # Check if the current user is authorized to edit this profile
    if request.user != user and not request.user.is_staff:
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce profil.")
        return redirect('center_panel:profile_detail', pk=profile.pk)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('center_panel:profile_detail', pk=profile.pk)
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
        'title': f'Modifier le profil de {user.get_full_name() or user.username}'
    }
    return render(request, 'center_panel/profiles/profile_form.html', context)

@login_required
def delete_profile(request, pk):
    """
    Delete a user profile.
    Only staff members can delete profiles.
    """
    if not request.user.is_staff:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer des profils.")
        return redirect('center_panel:profiles')
    
    profile = get_object_or_404(Profile, pk=pk)
    
    if request.method == 'POST':
        user = profile.user
        user.delete()  # This will also delete the profile due to CASCADE
        messages.success(request, 'Le profil a été supprimé avec succès.')
        return redirect('center_panel:profiles')
    
    return render(request, 'center_panel/profiles/profile_confirm_delete.html', {'profile': profile})

# Role CRUD Views
@login_required
def role_list(request):
    """Display all staff roles."""
    current_center = DocumentationCenter.objects.first()
    roles = Role.objects.all().order_by('name')
    
    context = {
        'roles': roles,
        'current_center': current_center,
    }
    return render(request, 'center_panel/admin/role_list.html', context)

@login_required
def add_role(request):
    """Add a new staff role."""
    current_center = DocumentationCenter.objects.first()
    
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rôle ajouté avec succès.')
            return redirect('center_panel:roles')
    else:
        form = RoleForm()
    
    context = {
        'form': form,
        'current_center': current_center,
        'is_add': True,
    }
    return render(request, 'center_panel/admin/add_edit_role.html', context)

@login_required
def edit_role(request, pk):
    """Edit an existing staff role."""
    current_center = DocumentationCenter.objects.first()
    role = get_object_or_404(Role, pk=pk)
    
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rôle modifié avec succès.')
            return redirect('center_panel:roles')
    else:
        form = RoleForm(instance=role)
    
    context = {
        'form': form,
        'role': role,
        'current_center': current_center,
        'is_add': False,
    }
    return render(request, 'center_panel/admin/add_edit_role.html', context)

@login_required
def delete_role(request, pk):
    """Delete a staff role."""
    role = get_object_or_404(Role, pk=pk)
    
    # Check if the role is associated with any staff members
    if Staff.objects.filter(role=role).exists():
        messages.error(request, 'Impossible de supprimer ce rôle car il est associé à des membres du personnel.')
    else:
        role.delete()
        messages.success(request, 'Rôle supprimé avec succès.')
    
    return redirect('center_panel:roles')

@login_required
def nubo_dashboard(request):
    """
    Displays the Nubo dashboard, showing the digitization status of all physical books.
    This is now the main entry point for the Nubo feature.
    """
    current_center = DocumentationCenter.objects.first()

    # Get all physical books and ensure a digitization record exists for each one
    physical_books = Book.objects.filter(documentation_center=current_center, is_digital=False)
    for book in physical_books:
        BookDigitization.objects.get_or_create(book=book)

    # Get all digitization records to display on the dashboard
    digitization_statuses = BookDigitization.objects.filter(
        book__documentation_center=current_center
    ).select_related('book').order_by('book__title')

    context = {
        'digitization_statuses': digitization_statuses,
        'current_center': current_center,
    }
    return render(request, 'center_panel/nubo_dashboard.html', context)


@login_required
def nubo_scan(request, book_id):
    """
    Handles the scanning interface for a specific book.
    Displays the current scanning progress and allows uploading new scanned pages.
    """
    try:
        book = Book.objects.get(id=book_id, is_digital=False)
        digitization_process, created = BookDigitization.objects.get_or_create(book=book)
    except Book.DoesNotExist:
        messages.error(request, "Le livre demandé n'existe pas ou n'est pas un livre physique.")
        return redirect('center_panel:nubo_dashboard')
    
    # Get all scanned pages for this book, ordered by page number
    scanned_pages = DigitizedPage.objects.filter(
        digitization_process=digitization_process
    ).order_by('page_number')
    
    # Handle page upload form
    if request.method == 'POST':
        # Check if this is a file upload
        if 'page_image' in request.FILES:
            # Determine the next page number
            next_page_number = digitization_process.last_scanned_page + 1
            
            # Create the new page
            new_page = DigitizedPage(
                digitization_process=digitization_process,
                page_number=next_page_number,
                image=request.FILES['page_image']
            )
            new_page.save()
            
            # Update the digitization process
            digitization_process.last_scanned_page = next_page_number
            if digitization_process.status == 'not_started':
                digitization_process.status = 'in_progress'
            digitization_process.save()
            
            messages.success(request, f"Page {next_page_number} ajoutée avec succès.")
            return redirect('center_panel:nubo_scan', book_id=book_id)
        
        # Check if this is a status update
        elif 'status' in request.POST:
            new_status = request.POST.get('status')
            if new_status in [choice[0] for choice in BookDigitization.DigitizationStatus.choices]:
                digitization_process.status = new_status
                digitization_process.save()
                messages.success(request, "Statut de numérisation mis à jour.")
            return redirect('center_panel:nubo_scan', book_id=book_id)
    
    # If the book doesn't have a pages count and we've scanned pages, update it
    if (book.pages is None or book.pages == 0) and digitization_process.last_scanned_page > 0:
        # If we're scanning, we should at least set the pages to what we've scanned so far
        # This can be manually updated later if needed
        book.pages = digitization_process.last_scanned_page
        book.save()
    
    context = {
        'book': book,
        'digitization_process': digitization_process,
        'scanned_pages': scanned_pages,
        'total_pages': digitization_process.last_scanned_page,
        'status_choices': BookDigitization.DigitizationStatus.choices,
    }
    return render(request, 'center_panel/nubo_scan.html', context)

@login_required
def nubo_view_book(request, book_id):
    """
    View a digitized book with page navigation.
    Allows browsing through all scanned pages of a book.
    """
    try:
        book = Book.objects.get(id=book_id)
        digitization_process = BookDigitization.objects.get(book=book)
    except (Book.DoesNotExist, BookDigitization.DoesNotExist):
        messages.error(request, "Le livre demandé n'existe pas ou n'a pas été numérisé.")
        return redirect('center_panel:nubo_dashboard')
    
    # Get all scanned pages for this book, ordered by page number
    scanned_pages = DigitizedPage.objects.filter(
        digitization_process=digitization_process
    ).order_by('page_number')
    
    if not scanned_pages.exists():
        messages.warning(request, "Ce livre n'a pas encore de pages numérisées.")
        return redirect('center_panel:nubo_scan', book_id=book_id)
    
    # Get the current page number from the query string, default to 1
    current_page_num = int(request.GET.get('page', 1))
    
    # Get the current page object, or the first page if the requested page doesn't exist
    try:
        current_page = scanned_pages.get(page_number=current_page_num)
    except DigitizedPage.DoesNotExist:
        current_page = scanned_pages.first()
        current_page_num = current_page.page_number
    
    # Calculate previous and next page numbers for navigation
    prev_page = scanned_pages.filter(page_number__lt=current_page_num).order_by('-page_number').first()
    next_page = scanned_pages.filter(page_number__gt=current_page_num).order_by('page_number').first()
    
    context = {
        'book': book,
        'digitization_process': digitization_process,
        'scanned_pages': scanned_pages,
        'current_page': current_page,
        'prev_page': prev_page,
        'next_page': next_page,
        'total_pages': digitization_process.last_scanned_page,
    }
    return render(request, 'center_panel/nubo_view_book.html', context)

@login_required
def nubo_download_book(request, book_id):
    """
    Generate and download a PDF containing all digitized pages of a book.
    """
    # Get the book and its digitization process
    book = get_object_or_404(Book, pk=book_id)
    try:
        digitization_process = BookDigitization.objects.get(book=book)
    except BookDigitization.DoesNotExist:
        messages.error(request, "Processus de numérisation introuvable pour ce livre.")
        return redirect('center_panel:nubo_dashboard')
    
    # Check if there are any scanned pages
    if digitization_process.last_scanned_page == 0:
        messages.error(request, "Ce livre n'a pas encore de pages numérisées.")
        return redirect('center_panel:nubo_scan', book_id=book.id)
    
    # Get all scanned pages in order
    scanned_pages = DigitizedPage.objects.filter(digitization_process=digitization_process).order_by('page_number')
    
    if not scanned_pages:
        messages.error(request, "Aucune page numérisée trouvée pour ce livre.")
        return redirect('center_panel:nubo_scan', book_id=book.id)
    
    # Create a PDF file in memory
    buffer = io.BytesIO()
    
    # Create the PDF object using the BytesIO buffer
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Create a temporary directory for processed images
    temp_dir = tempfile.mkdtemp(prefix='nubo_pdf_')
    temp_files = []
    
    try:
        # Add each scanned page to the PDF
        for page in scanned_pages:
            if os.path.exists(page.image.path):
                try:
                    # Open the image
                    img = Image.open(page.image.path)
                    
                    # Convert to grayscale
                    img = img.convert('L')
                    
                    # Apply sharpening filter
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(1.5)  # Increase sharpness by 50%
                    
                    # Save the processed image to a temporary file
                    temp_img_path = os.path.join(temp_dir, f"page_{page.page_number}_processed.jpg")
                    img.save(temp_img_path, quality=85, optimize=True)
                    temp_files.append(temp_img_path)
                    
                    # Calculate scaling to fit full width while maintaining aspect ratio
                    img_width, img_height = img.size
                    ratio = width / img_width  # Full width
                    new_width = width
                    new_height = img_height * ratio
                    
                    # Calculate position to center vertically
                    x_pos = 0  # Left align
                    y_pos = max(0, (height - new_height) / 2)  # Center vertically if possible
                    
                    # Draw the processed image on the PDF
                    p.drawImage(temp_img_path, x_pos, y_pos, width=new_width, height=new_height)
                    
                    # Add page number at the bottom
                    p.setFont("Helvetica", 10)
                    p.drawString(width/2 - 20, 30, f"Page {page.page_number}")
                    
                    # Add a new page for the next image
                    p.showPage()
                except Exception as e:
                    # Skip problematic images
                    continue
    
        # Save the PDF
        p.save()
        
        # Move to the beginning of the BytesIO buffer
        buffer.seek(0)
        
        # Create a filename for the PDF
        filename = f"{book.title.replace(' ', '_')}_numerise.pdf"
        
        # Return the PDF as a downloadable file
        return FileResponse(buffer, as_attachment=True, filename=filename, content_type='application/pdf')
    except Exception as e:
        # Handle any errors
        messages.error(request, f"Erreur lors de la génération du PDF: {str(e)}")
        return redirect('center_panel:nubo_view_book', book_id=book.id)
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        
        # Remove the temporary directory
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


@login_required
def admin_panel(request):
    """
    Custom admin panel for the documentation center management.
    This serves as a central hub for all administrative actions.
    """
    try:
        current_center = DocumentationCenter.objects.first()  # For dev purposes
        if not current_center:
            messages.error(request, "Aucun centre de documentation trouvé pour l'utilisateur actuel.")
            return redirect('admin:index')
            
        # Get counts for all major models
        stats = {
            'books_count': Book.objects.filter(documentation_center=current_center).count(),
            'members_count': Member.objects.filter(documentation_center=current_center).count(),
            'active_loans_count': Loan.objects.filter(
                book__documentation_center=current_center,
                return_date__isnull=True
            ).count(),
            'staff_count': Staff.objects.filter(documentation_center=current_center).count(),
            'archival_docs_count': ArchivalDocument.objects.filter(documentation_center=current_center).count(),
            'training_modules_count': TrainingModule.objects.filter(documentation_center=current_center).count(),
        }
        
        # Get recent activities
        recent_activities = Activity.objects.filter(
            documentation_center=current_center
        ).order_by('-created_at')[:5]
        
        # Get overdue loans
        overdue_loans = Loan.objects.filter(
            book__documentation_center=current_center,
            return_date__isnull=True,
            due_date__lt=timezone.now().date()
        ).select_related('book', 'member')[:5]
        
        context = {
            'current_center': current_center,
            'stats': stats,
            'recent_activities': recent_activities,
            'overdue_loans': overdue_loans,
        }
        
        return render(request, 'center_panel/admin_panel.html', context)
        
    except Exception as e:
        messages.error(request, f"Une erreur est survenue: {str(e)}")
        return redirect('center_panel:dashboard')


@login_required
def nubo_delete_page(request, page_id):
    """
    Delete a digitized page and update the page numbers of subsequent pages.
    """
    # Get the page to delete
    page = get_object_or_404(DigitizedPage, pk=page_id)
    digitization_process = page.digitization_process
    book_id = digitization_process.book.id
    deleted_page_number = page.page_number
    
    # Delete the page image file from storage
    if page.image and os.path.exists(page.image.path):
        try:
            os.remove(page.image.path)
        except Exception as e:
            # Log the error but continue with deletion
            print(f"Error deleting image file: {e}")
    
    # Delete the page from the database
    page.delete()
    
    # Update page numbers for all subsequent pages
    subsequent_pages = DigitizedPage.objects.filter(
        digitization_process=digitization_process,
        page_number__gt=deleted_page_number
    ).order_by('page_number')
    
    for subsequent_page in subsequent_pages:
        subsequent_page.page_number -= 1
        subsequent_page.save()
    
    # Update the last_scanned_page count
    if digitization_process.last_scanned_page > 0:
        digitization_process.last_scanned_page -= 1
        
        # If we deleted the last page and there are no more pages, reset status to not_started
        if digitization_process.last_scanned_page == 0:
            digitization_process.status = 'not_started'
            
        digitization_process.save()
    
    messages.success(request, f"Page {deleted_page_number} supprimée avec succès.")
    return redirect('center_panel:nubo_scan', book_id=book_id)