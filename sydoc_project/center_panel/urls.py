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
    path('staff/', views.staff_list, name='staff'),
    path('archives/', views.archive_list, name='archives'),
    path('trainings/', views.training_list, name='trainings'),
    path('notifications/', views.notification_list, name='notifications'),
]