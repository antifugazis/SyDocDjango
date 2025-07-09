# sydoc_project/center_panel/urls.py

from django.urls import path
from . import views

app_name = 'center_panel' # Namespace for this app's URLs

urlpatterns = [
    path('dashboard/', views.center_dashboard, name='dashboard'),
    path('books/', views.center_book_list, name='books'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:pk>/delete/', views.delete_book, name='delete_book'),
    path('members/', views.member_list, name='members'),
    path('loans/', views.loan_list, name='loans'),
    path('loans/add/', views.add_loan, name='add_loan'),
    path('loans/<int:loan_id>/return/', views.return_loan, name='return_loan'),
    path('staff/', views.staff_list, name='staff'),
    path('archives/', views.archive_list, name='archives'),
    path('trainings/', views.training_list, name='trainings'),
    path('notifications/', views.notification_list, name='notifications'),
    path('members/add/', views.add_member, name='add_member'),
    path('members/<int:pk>/edit/', views.edit_member, name='edit_member'),
    path('members/<int:pk>/delete/', views.delete_member, name='delete_member'),
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/<int:pk>/edit/', views.edit_staff, name='edit_staff'),
    path('staff/<int:pk>/delete/', views.delete_staff, name='delete_staff'),
    path('activities/', views.activity_list, name='activities'),
    path('activities/add/', views.add_activity, name='add_activity'),
    path('activities/<int:pk>/edit/', views.edit_activity, name='edit_activity'),
    path('activities/<int:pk>/delete/', views.delete_activity, name='delete_activity'),
    path('archives/add/', views.add_archive, name='add_archive'),
    path('archives/<int:pk>/edit/', views.edit_archive, name='edit_archive'),
    path('archives/<int:pk>/download/', views.download_archive, name='download_archive'),
    path('archives/<int:pk>/delete/', views.delete_archive, name='delete_archive'),
]