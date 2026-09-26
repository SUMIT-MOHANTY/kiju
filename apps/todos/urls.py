from django.urls import path

from .views import (
    TodoCreateView,
    TodoDeleteView,
    TodoListView,
    TodoToggleDoneView,
    TodoUpdateView,
    dashboard,
    create_todo,
    toggle_todo,
    update_todo,
    delete_todo,
    edit_todo_form,
    cancel_edit,
    filter_todos,
    sort_todos,
)

app_name = "todos"

urlpatterns = [
    # Main dashboard
    path("", TodoListView.as_view(), name="list"),
    path('dashboard/', dashboard, name='dashboard'),
    
    # CRUD operations
    path("create/", TodoCreateView.as_view(), name="create"),
    path('create-func/', create_todo, name='create_func'),
    path("<int:pk>/update/", TodoUpdateView.as_view(), name="update"),
    path('<int:todo_id>/update-func/', update_todo, name='update_func'),
    path("<int:pk>/delete/", TodoDeleteView.as_view(), name="delete"),
    path('<int:todo_id>/delete-func/', delete_todo, name='delete_func'),
    path("<int:pk>/toggle/", TodoToggleDoneView.as_view(), name="toggle_done"),
    path('<int:todo_id>/toggle-func/', toggle_todo, name='toggle_func'),
    
    # Edit mode
    path('<int:todo_id>/edit/', edit_todo_form, name='edit'),
    path('<int:todo_id>/row/', cancel_edit, name='row'),
    
    # Filter and sort
    path('filter/', filter_todos, name='filter'),
    path('sort/', sort_todos, name='sort'),
]
