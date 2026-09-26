from django.utils import timezone
from .models import Todo

from typing import Optional
from django.db.models import QuerySet
from django.core.exceptions import ValidationError

from apps.todos.models import Todo


def create_todo(
    user,
    title: str,
    description: str = "",
    is_completed: bool = False
) -> Todo:
    """
    Create a new todo for a user.

    Args:
        user: The user who owns the todo
        title: The title of the todo
        description: Optional description
        is_completed: Initial completion status

    Returns:
        The created Todo instance

    Raises:
        ValidationError: If title is empty
    """
    if not title or not title.strip():
        raise ValidationError("Title is required")

    todo = Todo.objects.create(
        user=user,
        title=title.strip(),
        description=description.strip() if description else "",
        is_completed=is_completed,
        is_active=True
    )
    return todo


def update_todo(
    todo_id: int,
    user,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_completed: Optional[bool] = None
) -> Todo:
    """
    Update a todo's fields.

    Args:
        todo_id: The ID of the todo to update
        user: The user making the request (for isolation check)
        title: New title (optional)
        description: New description (optional)
        is_completed: New completion status (optional)

    Returns:
        The updated Todo instance

    Raises:
        Todo.DoesNotExist: If todo not found or not owned by user
    """
    try:
        todo = Todo.objects.get(id=todo_id, user=user, is_active=True)
    except Todo.DoesNotExist:
        raise Todo.DoesNotExist("Todo not found")

    update_fields = ['updated_at']

    if title is not None:
        if not title.strip():
            raise ValidationError("Title cannot be empty")
        todo.title = title.strip()
        update_fields.append('title')

    if description is not None:
        todo.description = description.strip() if description else ""
        update_fields.append('description')

    if is_completed is not None:
        todo.is_completed = is_completed
        update_fields.append('is_completed')

    todo.save(update_fields=update_fields)
    return todo


def toggle_status(todo_id: int, user) -> Todo:
    """
    Toggle the completion status of a todo.

    Args:
        todo_id: The ID of the todo
        user: The user making the request (for isolation check)

    Returns:
        The updated Todo instance

    Raises:
        Todo.DoesNotExist: If todo not found or not owned by user
    """
    try:
        todo = Todo.objects.get(id=todo_id, user=user, is_active=True)
    except Todo.DoesNotExist:
        raise Todo.DoesNotExist("Todo not found")

    todo.is_completed = not todo.is_completed
    todo.save(update_fields=['is_completed', 'updated_at'])
    return todo


def delete_todo(todo_id: int, user) -> None:
    """
    Soft delete a todo (sets is_active to False).

    Args:
        todo_id: The ID of the todo to delete
        user: The user making the request (for isolation check)

    Raises:
        Todo.DoesNotExist: If todo not found or not owned by user
    """
    try:
        todo = Todo.objects.get(id=todo_id, user=user, is_active=True)
    except Todo.DoesNotExist:
        raise Todo.DoesNotExist("Todo not found")

    todo.soft_delete()


def get_user_todos(
    user,
    status: Optional[str] = None,
    sort_by: str = "-created_at",
    include_deleted: bool = False
) -> QuerySet:
    """
    Get todos for a user with optional filtering and sorting.

    Args:
        user: The user whose todos to retrieve
        status: Filter by status - 'completed', 'pending', or None for all
        sort_by: Field to sort by (default: -created_at)
        include_deleted: If True, include soft-deleted todos

    Returns:
        QuerySet of Todo instances
    """
    queryset = Todo.objects.filter(user=user)

    if not include_deleted:
        queryset = queryset.filter(is_active=True)

    if status == "completed":
        queryset = queryset.filter(is_completed=True)
    elif status == "pending":
        queryset = queryset.filter(is_completed=False)

    # Validate sort_by to prevent injection
    allowed_sort_fields = [
        "created_at", "-created_at",
        "updated_at", "-updated_at",
        "title", "-title",
        "is_completed", "-is_completed"
    ]
    if sort_by in allowed_sort_fields:
        queryset = queryset.order_by(sort_by)
    else:
        queryset = queryset.order_by("-created_at")

    return queryset
