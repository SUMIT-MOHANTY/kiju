"""
HTMX-enabled Todo Views

This module provides all views for the Todo dashboard with HTMX integration.
All endpoints return HTML partials for seamless client-side updates.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

from .models import Todo
from .services import (
    create_todo,
    update_todo,
    toggle_status,
    delete_todo,
    get_user_todos
)


class HtmxMixin:
    """Mixin to detect HTMX requests."""

    def is_htmx_request(self, request):
        return request.headers.get('HX-Request') == 'true'


class TodoListView(LoginRequiredMixin, HtmxMixin, ListView):
    """
    List view for todos with filtering and sorting support.
    Returns HTML partial for HTMX requests, full page otherwise.
    """
    model = Todo
    template_name = 'todos/todo_list.html'
    context_object_name = 'todos'
    partial_template_name = 'todos/partials/todo_list.html'

    def get_queryset(self):
        """Get todos for the current user with filtering and sorting."""
        completed = self.request.GET.get('completed')
        ordering = self.request.GET.get('ordering', '-created_at')

        return get_user_todos(
            user=self.request.user,
            completed=completed,
            ordering=ordering
        )

    def get_template_names(self):
        """Return partial template for HTMX requests."""
        if self.is_htmx_request(self.request):
            return [self.partial_template_name]
        return [self.template_name]


@method_decorator(ratelimit(key='ip', rate='5/m', method=['POST']), name='dispatch')
class TodoCreateView(LoginRequiredMixin, HtmxMixin, View):
    """
    Create view for todos.
    Rate limited to 5 requests per minute per IP.
    Returns HTML partial of new todo row for HTMX.
    """

    def post(self, request, *args, **kwargs):
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()

        if not title:
            if self.is_htmx_request(request):
                return HttpResponseBadRequest("Title is required")
            messages.error(request, "Title is required")
            return redirect('todos:list')

        try:
            todo = create_todo(
                user=request.user,
                title=title,
                description=description
            )

            if self.is_htmx_request(request):
                return render(request, 'todos/partials/todo_row.html', {'todo': todo})

            messages.success(request, "Todo created successfully")
            return redirect('todos:list')

        except ValidationError as e:
            if self.is_htmx_request(request):
                return HttpResponseBadRequest(str(e))
            messages.error(request, str(e))
            return redirect('todos:list')


@method_decorator(ratelimit(key='ip', rate='5/m', method=['PATCH', 'POST']), name='dispatch')
class TodoUpdateView(LoginRequiredMixin, HtmxMixin, View):
    """
    Update view for todos (inline edit).
    Rate limited to 5 requests per minute per IP.
    Returns editable form for GET, updated display for PATCH/POST.
    """

    def get(self, request, pk, *args, **kwargs):
        """Return editable form for inline editing."""
        todo = get_object_or_404(Todo, pk=pk, is_active=True)

        # Enforce user-scoped data isolation
        if todo.user != request.user:
            raise PermissionDenied("You don't have permission to edit this todo")

        if self.is_htmx_request(request):
            return render(request, 'todos/partials/todo_edit_form.html', {'todo': todo})

        return render(request, 'todos/todo_form.html', {'todo': todo})

    def patch(self, request, pk, *args, **kwargs):
        """Handle PATCH request for inline update."""
        return self.post(request, pk, *args, **kwargs)

    def post(self, request, pk, *args, **kwargs):
        """Update todo and return updated display."""
        todo = get_object_or_404(Todo, pk=pk, is_active=True)

        # Enforce user-scoped data isolation
        if todo.user != request.user:
            raise PermissionDenied("You don't have permission to edit this todo")

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()

        try:
            updated_todo = update_todo(
                todo_id=todo.id,
                user=request.user,
                title=title if title else None,
                description=description if description else None
            )

            if self.is_htmx_request(request):
                return render(request, 'todos/partials/todo_row.html', {'todo': updated_todo})

            messages.success(request, "Todo updated successfully")
            return redirect('todos:list')

        except ValidationError as e:
            if self.is_htmx_request(request):
                return HttpResponseBadRequest(str(e))
            messages.error(request, str(e))
            return redirect('todos:list')


@method_decorator(ratelimit(key='ip', rate='5/m', method=['PATCH', 'POST']), name='dispatch')
class TodoToggleView(LoginRequiredMixin, HtmxMixin, View):
    """
    Toggle view for todo completion status.
    Rate limited to 5 requests per minute per IP.
    Returns updated status badge and completion timestamp.
    """

    def patch(self, request, pk, *args, **kwargs):
        """Toggle todo status via PATCH."""
        return self.post(request, pk, *args, **kwargs)

    def post(self, request, pk, *args, **kwargs):
        """Toggle todo completion status."""
        todo = get_object_or_404(Todo, pk=pk, is_active=True)

        # Enforce user-scoped data isolation
        if todo.user != request.user:
            raise PermissionDenied("You don't have permission to modify this todo")

        toggled_todo = toggle_status(todo_id=todo.id, user=request.user)

        if self.is_htmx_request(request):
            return render(request, 'todos/partials/todo_status.html', {
                'todo': toggled_todo,
                'completed_at': toggled_todo.completed_at
            })

        status = "completed" if toggled_todo.is_completed else "active"
        messages.success(request, f"Todo marked as {status}")
        return redirect('todos:list')


@method_decorator(ratelimit(key='ip', rate='5/m', method=['DELETE', 'POST']), name='dispatch')
class TodoDeleteView(LoginRequiredMixin, HtmxMixin, View):
    """
    Delete view for todos (soft delete).
    Rate limited to 5 requests per minute per IP.
    Returns empty swap with HX-Trigger for toast notification.
    """

    def delete(self, request, pk, *args, **kwargs):
        """Soft delete todo via DELETE request."""
        return self._delete_todo(request, pk)

    def post(self, request, pk, *args, **kwargs):
        """Handle POST with _method=DELETE for form submissions."""
        if request.POST.get('_method') == 'DELETE':
            return self._delete_todo(request, pk)
        return HttpResponseBadRequest("Invalid method")

    def _delete_todo(self, request, pk):
        """Perform soft delete."""
        todo = get_object_or_404(Todo, pk=pk, is_active=True)

        # Enforce user-scoped data isolation
        if todo.user != request.user:
            raise PermissionDenied("You don't have permission to delete this todo")

        delete_todo(todo_id=todo.id, user=request.user)

        if self.is_htmx_request(request):
            # Return empty response with HX-Trigger header for toast
            response = HttpResponse('')
            response['HX-Trigger'] = '{"showToast": {"message": "Todo deleted successfully", "type": "success"}}'
            return response

        messages.success(request, "Todo deleted successfully")
        return redirect('todos:list')


# Legacy function-based views for backward compatibility

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
