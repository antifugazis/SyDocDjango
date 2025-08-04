# sydoc_project/center_panel/urls.py

from django.urls import path
from . import views
from . import log_views
from . import views_debug
from . import views_group_test
from . import views_login

app_name = 'center_panel' # Namespace for this app's URLs

urlpatterns = [
    # Dashboard
    path('dashboard/', views.center_dashboard, name='dashboard'),
    path('doc-center-dashboard/', views.doc_center_dashboard, name='doc_center_dashboard'),

    # Book Management
    path('books/', views.center_book_list, name='books'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:pk>/delete/', views.delete_book, name='delete_book'),
    path('books/<int:book_id>/like/', views.like_book, name='like_book'),
    path('books/<int:book_id>/dislike/', views.dislike_book, name='dislike_book'),
    path('books/<int:book_id>/mark-as-read/', views.mark_book_as_read, name='mark_book_as_read'),

    # Member Management
    path('members/', views.member_list, name='members'),
    path('members/add/', views.add_member, name='add_member'),
    path('members/<int:pk>/edit/', views.edit_member, name='edit_member'),
    path('members/<int:pk>/delete/', views.delete_member, name='delete_member'),
    path('members/<int:member_id>/suspend/', views.suspend_member, name='suspend_member'),
    path('members/<int:member_id>/unsuspend/', views.unsuspend_member, name='unsuspend_member'),

    # Loan Management
    path('loans/', views.loan_list, name='loans'),
    path('loans/add/', views.add_loan, name='add_loan'),
    path('loans/<int:loan_id>/edit/', views.edit_loan, name='edit_loan'),
    path('loans/<int:loan_id>/return/', views.return_loan, name='return_loan'),
    path('loans/<int:loan_id>/approve/', views.approve_loan, name='approve_loan'),
    path('loans/<int:loan_id>/reject/', views.reject_loan, name='reject_loan'),
    path('loans/<int:loan_id>/cancel/', views.cancel_loan, name='cancel_loan'),
    path('loans/<int:loan_id>/delete/', views.delete_loan, name='delete_loan'),
    
    # Member loans (for members to view their own loans)
    path('my-loans/', views.my_loans, name='my_loans'),
    path('spiritual_resources/', views.spiritual_resources, name='spiritual_resources'),
    path('member-loans/', views.member_loans, name='member_loans'),
    
    # API Endpoints
    path('api/books/<int:book_id>/details/', views.get_book_details, name='book_details_api'),
    path('api/members/<int:member_id>/details/', views.get_member_details, name='member_details_api'),

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
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),

    # Activity Management
    path('activities/', views.activity_list, name='activities'),
    path('activities/add/', views.add_activity, name='add_activity'),
    path('activities/<int:pk>/edit/', views.edit_activity, name='edit_activity'),
    path('activities/<int:pk>/delete/', views.delete_activity, name='delete_activity'),
    path('activities/<int:pk>/suspend/', views.suspend_activity, name='suspend_activity'),
    path('activities/<int:pk>/restore/', views.restore_activity, name='restore_activity'),
    
    # Chat System
    path('chat/', views.chat_inbox, name='chat_inbox'),
    path('chat/<int:user_id>/', views.chat_conversation, name='chat_conversation'),
    path('chat/send/', views.send_new_message, name='send_new_message'),

    # Communiques
    path('communiques/', views.communique_list, name='communiques'),
    path('communiques/add/', views.add_communique, name='add_communique'),
    path('communiques/<int:pk>/', views.communique_detail, name='communique_detail'),
    path('communiques/<int:pk>/edit/', views.edit_communique, name='edit_communique'),
    path('communiques/<int:pk>/delete/', views.delete_communique, name='delete_communique'),
    path('communiques/<int:pk>/view/', views.increment_view_communique, name='increment_view_communique'),
    path('communiques/<int:pk>/reaction/', views.communique_reaction, name='communique_reaction'),

    # Quiz & Results
    path('results/<int:pk>/', views.quiz_results, name='quiz_results'),

    # API Endpoints
    path('api/lessons/<int:pk>/quiz/', views.lesson_quiz_api, name='lesson_quiz_api'),
    path('api/subgenres/', views.api_subgenres, name='api_subgenres'),
    path('api/subthemes/', views.api_subthemes, name='api_subthemes'),
    
    # Genre Management
    path('literary-genres/', views.literary_genre_list, name='literary_genres'),
    path('literary-genres/add/', views.add_literary_genre, name='add_literary_genre'),
    path('literary-genres/<int:pk>/edit/', views.edit_literary_genre, name='edit_literary_genre'),
    path('literary-genres/<int:pk>/delete/', views.delete_literary_genre, name='delete_literary_genre'),
    
    # Sub-Genre Management
    path('sub-genres/', views.subgenre_list, name='subgenres'),
    path('sub-genres/add/', views.add_subgenre, name='add_subgenre'),
    path('sub-genres/<int:pk>/edit/', views.edit_subgenre, name='edit_subgenre'),
    path('sub-genres/<int:pk>/delete/', views.delete_subgenre, name='delete_subgenre'),
    
    # Theme Management
    path('themes/', views.theme_list, name='themes'),
    path('themes/add/', views.add_theme, name='add_theme'),
    path('themes/<int:pk>/edit/', views.edit_theme, name='edit_theme'),
    path('themes/<int:pk>/delete/', views.delete_theme, name='delete_theme'),
    
    # Language Management
    path('languages/', views.language_list, name='language_list'),
    path('languages/add/', views.add_language, name='add_language'),
    path('languages/<int:pk>/edit/', views.edit_language, name='edit_language'),
    path('languages/<int:pk>/delete/', views.delete_language, name='delete_language'),
    
    # Sub-Theme Management
    path('sub-themes/', views.subtheme_list, name='subthemes'),
    path('sub-themes/add/', views.add_subtheme, name='add_subtheme'),
    path('sub-themes/<int:pk>/edit/', views.edit_subtheme, name='edit_subtheme'),
    path('sub-themes/<int:pk>/delete/', views.delete_subtheme, name='delete_subtheme'),
    
    # Debug URLs
    path('debug/media-config/', views_debug.DebugMediaConfigView.as_view(), name='debug_media_config'),
    path('debug/upload/', views_debug.debug_upload, name='debug_upload'),
    
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
    
    # Complaints Management
    path('complaints/', views.admin_complaints, name='admin_complaints'),
    path('complaints/<int:complaint_id>/resolve/', views.resolve_complaint, name='resolve_complaint'),
    
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
    
    # Group Testing Views
    path('group-info/', views_group_test.group_info, name='group_info'),
    path('group-info/api/', views_group_test.group_info_api, name='group_info_api'),
    path('group-protected/', views_group_test.group_protected_view, name='group_protected_view'),
    
    # Login Success - Group-based redirect
    path('login-success/', views_login.login_success, name='login_success'),
    
    # Help Center
    path('help-center/', views.help_center, name='help_center'),
]
