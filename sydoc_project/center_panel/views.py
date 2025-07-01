from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import DocumentationCenter, Book, Member, Loan, Staff, ArchivalDocument, TrainingModule
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
    }
    
    # Recent Loans (last 5)
    recent_loans = Loan.objects.filter(
        book__documentation_center=current_center
    ).order_by('-loan_date')[:5]
    
    # Add is_overdue flag to each loan
    for loan in recent_loans:
        loan.is_overdue = loan.due_date < timezone.localdate() and loan.status in ['borrowed', 'overdue']
    
    # Upcoming Returns (next 5 due)
    upcoming_returns = Loan.objects.filter(
        book__documentation_center=current_center,
        status__in=['borrowed', 'overdue'],
        return_date__isnull=True
    ).order_by('due_date')[:5]
    
    # Add days_left to each upcoming return
    for loan in upcoming_returns:
        loan.days_left = (loan.due_date - timezone.localdate()).days
    
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
def add_book(request):
    # Get the current center
    current_center = DocumentationCenter.objects.first()
    if not current_center:
        messages.error(request, "Aucun centre de documentation trouvé.")
        return redirect('admin:index')
        
    context = {
        'current_center': current_center
    }
    return render(request, 'center_panel/add_book.html', context)

@login_required
def book_detail(request, pk):
    # Get the current center
    current_center = DocumentationCenter.objects.first()
    if not current_center:
        messages.error(request, "Aucun centre de documentation trouvé.")
        return redirect('admin:index')
        
    # Get the book
    book = get_object_or_404(Book, pk=pk, documentation_center=current_center)
    
    context = {
        'current_center': current_center,
        'book': book
    }
    return render(request, 'center_panel/book_detail.html', context)

@login_required
def edit_book(request, pk):
    # Get the current center
    current_center = DocumentationCenter.objects.first()
    if not current_center:
        messages.error(request, "Aucun centre de documentation trouvé.")
        return redirect('admin:index')
        
    # Get the book
    book = get_object_or_404(Book, pk=pk, documentation_center=current_center)
    
    context = {
        'current_center': current_center,
        'book': book
    }
    return render(request, 'center_panel/edit_book.html', context)

@login_required
def delete_book(request, pk):
    # Get the current center
    current_center = DocumentationCenter.objects.first()
    if not current_center:
        messages.error(request, "Aucun centre de documentation trouvé.")
        return redirect('admin:index')
        
    # Get the book
    book = get_object_or_404(Book, pk=pk, documentation_center=current_center)
    
    # Delete the book (in a real app, you'd confirm this action)
    book.delete()
    messages.success(request, f"Le livre '{book.title}' a été supprimé avec succès.")
    
    return redirect('center_panel:books')

@login_required
def member_list(request):
    # Get the current center
    current_center = DocumentationCenter.objects.first()
    if not current_center:
        messages.error(request, "Aucun centre de documentation trouvé.")
        return redirect('admin:index')
        
    # Get members for this center
    members = Member.objects.filter(documentation_center=current_center)
    
    context = {
        'current_center': current_center,
        'members': members
    }
    return render(request, 'center_panel/members.html', context)

@login_required
def loan_list(request):
    # Get the current center
    current_center = DocumentationCenter.objects.first()
    if not current_center:
        messages.error(request, "Aucun centre de documentation trouvé.")
        return redirect('admin:index')
        
    # Get loans for this center through the Book relationship
    loans = Loan.objects.filter(book__documentation_center=current_center)
    
    context = {
        'current_center': current_center,
        'loans': loans
    }
    return render(request, 'center_panel/loans.html', context)

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