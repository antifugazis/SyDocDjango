import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

@login_required
@user_passes_test(lambda u: u.is_superuser)
def view_logs(request):
    """
    Display system logs for superusers only.
    Shows the contents of the Django log file with pagination.
    """
    log_file_path = os.path.join(settings.LOGS_DIR, "django.log")
    log_content = ""
    log_exists = os.path.exists(log_file_path)
    
    if log_exists:
        try:
            with open(log_file_path, "r") as f:
                # Read the file and reverse the lines to show newest logs first
                log_lines = f.readlines()
                log_lines.reverse()  # Newest logs first
                
                # Simple pagination
                page = request.GET.get('page', 1)
                page = int(page)
                per_page = 100  # Lines per page
                total_lines = len(log_lines)
                total_pages = (total_lines + per_page - 1) // per_page
                
                start_idx = (page - 1) * per_page
                end_idx = min(start_idx + per_page, total_lines)
                
                # Get the current page's lines
                current_lines = log_lines[start_idx:end_idx]
                log_content = ''.join(current_lines)
                
        except Exception as e:
            log_content = f"Une erreur s'est produite lors de la lecture du fichier journal: {str(e)}"
    else:
        log_content = "Le fichier journal n'existe pas encore. Il sera créé lorsque des événements seront enregistrés."
    
    context = {
        'log_content': log_content,
        'log_exists': log_exists,
        'current_page': page if log_exists else 1,
        'total_pages': total_pages if log_exists else 1,
        'has_next': page < total_pages if log_exists else False,
        'has_prev': page > 1 if log_exists else False,
        'next_page': page + 1 if log_exists and page < total_pages else None,
        'prev_page': page - 1 if log_exists and page > 1 else None,
    }
    
    return render(request, 'center_panel/admin/logs.html', context)
