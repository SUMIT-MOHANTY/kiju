"""
URL configuration for the todos app.
Defines HTMX-enabled endpoints for todo CRUD operations.
"""
from django.urls import path
from . import views


app_name = 'todos'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard, name='dashboard'),
    
    # CRUD operations
    path('create/', views.create_todo, name='create'),
    path('<int:todo_id>/toggle/', views.toggle_todo, name='toggle'),
    path('<int:todo_id>/update/', views.update_todo, name='update'),
    path('<int:todo_id>/delete/', views.delete_todo, name='delete'),
    
    # Edit mode
    path('<int:todo_id>/edit/', views.edit_todo_form, name='edit'),
    path('<int:todo_id>/row/', views.cancel_edit, name='row'),
    
    # Filter and sort
    path('filter/', views.filter_todos, name='filter'),
    path('sort/', views.sort_todos, name='sort'),
]
