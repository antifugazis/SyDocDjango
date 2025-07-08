from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import DocumentationCenter, Book, Member, Loan, Staff, ArchivalDocument, TrainingModule
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .forms import BookForm, MemberForm, CreateLoanForm, StaffForm

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