# sydoc_project/center_panel/urls.py

from django.urls import path
from . import views
from . import log_views

app_name = 'center_panel' # Namespace for this app's URLs

urlpatterns = [
    # Dashboard
    path('dashboard/', views.center_dashboard, name='dashboard'),

    # Book Management
    path('books/', views.center_book_list, name='books'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:pk>/delete/', views.delete_book, name='delete_book'),

    # Member Management
    path('members/', views.member_list, name='members'),
    path('members/add/', views.add_member, name='add_member'),
    path('members/<int:pk>/edit/', views.edit_member, name='edit_member'),
    path('members/<int:pk>/delete/', views.delete_member, name='delete_member'),

    # Loan Management
    path('loans/', views.loan_list, name='loans'),
    path('loans/add/', views.add_loan, name='add_loan'),
    path('loans/<int:loan_id>/return/', views.return_loan, name='return_loan'),

    # Staff Management
    path('staff/', views.staff_list, name='staff'),
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/<int:pk>/edit/', views.edit_staff, name='edit_staff'),
    path('staff/<int:pk>/delete/', views.delete_staff, name='delete_staff'),

    # Archive Management
    path('archives/', views.archive_list, name='archives'),
    path('archives/add/', views.add_archive, name='add_archive'),
    path('archives/<int:pk>/edit/', views.edit_archive, name='edit_archive'),
    path('archives/<int:pk>/download/', views.download_archive, name='download_archive'),
    path('archives/<int:pk>/delete/', views.delete_archive, name='delete_archive'),

    # Training Subjects
    path('training_subjects/', views.training_subject_list, name='training_subjects'),
    path('training_subjects/add/', views.add_training_subject, name='add_training_subject'),
    path('training_subjects/<int:pk>/edit/', views.edit_training_subject, name='edit_training_subject'),
    path('training_subjects/<int:pk>/delete/', views.delete_training_subject, name='delete_training_subject'),

    # Training Modules
    path('trainings/', views.training_list, name='trainings'),
    path('trainings/add/', views.add_training_module, name='add_training'),
    path('trainings/<int:pk>/', views.training_detail, name='training_detail'),
    path('trainings/<int:pk>/edit/', views.edit_training_module, name='edit_training_module'),
    path('trainings/<int:pk>/delete/', views.delete_training_module, name='delete_training_module'),

    # Lessons
    path('lessons/', views.lesson_list, name='lesson_list'),
    path('lessons/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:pk>/quiz/', views.lesson_quiz, name='lesson_quiz'),

    # Notifications
    path('notifications/', views.notification_list, name='notifications'),

    # Activity Management
    path('activities/', views.activity_list, name='activities'),
    path('activities/add/', views.add_activity, name='add_activity'),
    path('activities/<int:pk>/edit/', views.edit_activity, name='edit_activity'),
    path('activities/<int:pk>/delete/', views.delete_activity, name='delete_activity'),

    # Communiques
    path('communiques/', views.communique_list, name='communiques'),
    path('communiques/add/', views.add_communique, name='add_communique'),
    path('communiques/<int:pk>/', views.communique_detail, name='communique_detail'),

    # Quiz & Results
    path('results/<int:pk>/', views.quiz_results, name='quiz_results'),

    # API Endpoints
    path('api/lessons/<int:pk>/quiz/', views.lesson_quiz_api, name='lesson_quiz_api'),
    
    # Category Management
    path('categories/', views.category_list, name='categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    
    # Author Management
    path('authors/', views.author_list, name='authors'),
    path('authors/add/', views.add_author, name='add_author'),
    path('authors/<int:pk>/edit/', views.edit_author, name='edit_author'),
    path('authors/<int:pk>/delete/', views.delete_author, name='delete_author'),
    
    # Role Management
    path('roles/', views.role_list, name='roles'),
    path('roles/add/', views.add_role, name='add_role'),
    path('roles/<int:pk>/edit/', views.edit_role, name='edit_role'),
    path('roles/<int:pk>/delete/', views.delete_role, name='delete_role'),
    
    # Profile Management
    path('profiles/', views.profile_list, name='profiles'),
    path('profiles/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('profiles/<int:pk>/edit/', views.edit_profile, name='edit_profile'),
    path('profiles/<int:pk>/delete/', views.delete_profile, name='delete_profile'),
    
    # Admin Panel
    path('admin/', views.admin_panel, name='admin_panel'),
    
    # Nubo Digitization Features
    path('nubo/', views.nubo_dashboard, name='nubo_dashboard'),
    path('nubo/scan/<int:book_id>/', views.nubo_scan, name='nubo_scan'),
    path('nubo/view/<int:book_id>/', views.nubo_view_book, name='nubo_view_book'),
    path('nubo/download/<int:book_id>/', views.nubo_download_book, name='nubo_download_book'),
    path('nubo/delete-page/<int:page_id>/', views.nubo_delete_page, name='nubo_delete_page'),
    
    # Admin Features
    path('admin/logs/', log_views.view_logs, name='logs'),
]
