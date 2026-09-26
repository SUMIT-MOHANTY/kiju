from django.conf import settings
from django.db import models

from apps.core.models import TimestampedBaseModel


class Todo(TimestampedBaseModel):
    """
    Todo model extending TimestampedBaseModel with user FK, title, description,
    is_completed, and soft delete via is_active.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='todos',
        help_text='The user who owns this todo'
    )
    title = models.CharField(
        max_length=255,
        help_text='The title of the todo'
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text='Optional description of the todo'
    )
    is_completed = models.BooleanField(
        default=False,
        help_text='Whether the todo is completed'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Soft delete flag - False means deleted'
    )

    class Meta:
        db_table = 'todos_todo'
        ordering = ['-created_at']
        verbose_name = 'Todo'
        verbose_name_plural = 'Todos'

    def __str__(self):
        return self.title

    def soft_delete(self):
        """Soft delete the todo by setting is_active to False."""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])

    def restore(self):
        """Restore a soft-deleted todo by setting is_active to True."""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])
