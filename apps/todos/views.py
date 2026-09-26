"""
HTMX-enabled Todo Views

This module provides all views for the Todo dashboard with HTMX integration.
All endpoints return HTML partials for seamless client-side updates.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone

from .models import Todo


@login_required
def dashboard(request):
    """
    Main todo dashboard page.
    Returns full HTML page with all todos for the authenticated user.
    """
    todos = Todo.objects.filter(user=request.user, is_active=True)
    
    # Get filter from query params
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'completed':
        todos = todos.filter(is_completed=True)
    elif status_filter == 'pending':
        todos = todos.filter(is_completed=False)
    
    # Get sort order from query params
    sort_order = request.GET.get('order', 'newest')
    if sort_order == 'oldest':
        todos = todos.order_by('created_at')
    else:
        todos = todos.order_by('-created_at')
    
    context = {
        'todos': todos,
        'status_filter': status_filter,
        'sort_order': sort_order,
        'todos_count': todos.count(),
    }
    
    return render(request, 'todos/dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def create_todo(request):
    """
    Create a new todo item.
    HTMX endpoint - returns the new todo row HTML.
    """
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    
    if not title:
        return HttpResponseBadRequest("Title is required")
    
    todo = Todo.objects.create(
        user=request.user,
        title=title,
        description=description,
        is_completed=False,
        is_active=True
    )
    
    # Return just the new row for HTMX to insert
    return render(request, 'todos/partials/todo_row.html', {'todo': todo})


@login_required
@require_http_methods(["PATCH", "POST"])
def toggle_todo(request, todo_id):
    """
    Toggle the completion status of a todo.
    HTMX endpoint - returns updated row HTML.
    """
    todo = get_object_or_404(Todo, id=todo_id, user=request.user, is_active=True)
    
    # Toggle completion status
    todo.is_completed = not todo.is_completed
    todo.save()
    
    return render(request, 'todos/partials/todo_row.html', {'todo': todo})


@login_required
@require_http_methods(["PATCH", "POST"])
def update_todo(request, todo_id):
    """
    Update todo title and description.
    HTMX endpoint - returns display row HTML.
    """
    todo = get_object_or_404(Todo, id=todo_id, user=request.user, is_active=True)
    
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    
    if not title:
        return HttpResponseBadRequest("Title is required")
    
    todo.title = title
    todo.description = description
    todo.save()
    
    return render(request, 'todos/partials/todo_row.html', {'todo': todo})


@login_required
@require_http_methods(["DELETE", "POST"])
def delete_todo(request, todo_id):
    """
    Soft delete a todo item.
    HTMX endpoint - returns empty response (triggers swap delete).
    """
    todo = get_object_or_404(Todo, id=todo_id, user=request.user, is_active=True)
    todo.soft_delete()
    
    # Return empty response for HTMX to delete the row
    return HttpResponse('')


@login_required
@require_http_methods(["GET"])
def edit_todo_form(request, todo_id):
    """
    Return the inline edit form for a todo row.
    HTMX endpoint - returns edit form HTML.
    """
    todo = get_object_or_404(Todo, id=todo_id, user=request.user, is_active=True)
    return render(request, 'todos/partials/todo_row_edit.html', {'todo': todo})


@login_required
@require_http_methods(["GET"])
def cancel_edit(request, todo_id):
    """
    Cancel editing and return to display mode.
    HTMX endpoint - returns display row HTML.
    """
    todo = get_object_or_404(Todo, id=todo_id, user=request.user, is_active=True)
    return render(request, 'todos/partials/todo_row.html', {'todo': todo})


@login_required
@require_http_methods(["GET"])
def filter_todos(request):
    """
    Filter todos by status.
    HTMX endpoint - returns filtered list HTML.
    """
    status_filter = request.GET.get('status', 'all')
    todos = Todo.objects.filter(user=request.user, is_active=True)
    
    if status_filter == 'completed':
        todos = todos.filter(is_completed=True)
    elif status_filter == 'pending':
        todos = todos.filter(is_completed=False)
    
    # Apply current sort
    sort_order = request.GET.get('order', 'newest')
    if sort_order == 'oldest':
        todos = todos.order_by('created_at')
    else:
        todos = todos.order_by('-created_at')
    
    context = {
        'todos': todos,
        'status_filter': status_filter,
        'sort_order': sort_order,
    }
    
    return render(request, 'todos/partials/todo_list.html', context)


@login_required
@require_http_methods(["GET"])
def sort_todos(request):
    """
    Sort todos by date.
    HTMX endpoint - returns sorted list HTML.
    """
    sort_order = request.GET.get('order', 'newest')
    todos = Todo.objects.filter(user=request.user, is_active=True)
    
    # Apply current filter
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'completed':
        todos = todos.filter(is_completed=True)
    elif status_filter == 'pending':
        todos = todos.filter(is_completed=False)
    
    if sort_order == 'oldest':
        todos = todos.order_by('created_at')
    else:
        todos = todos.order_by('-created_at')
    
    context = {
        'todos': todos,
        'status_filter': status_filter,
        'sort_order': sort_order,
    }
    
    return render(request, 'todos/partials/todo_list.html', context)


@login_required
@require_http_methods(["GET"])
def get_todo_row(request, todo_id):
    """
    Get a single todo row (for refresh/cancel operations).
    HTMX endpoint - returns display row HTML.
    """
    todo = get_object_or_404(Todo, id=todo_id, user=request.user, is_active=True)
    return render(request, 'todos/partials/todo_row.html', {'todo': todo})
