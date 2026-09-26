from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel
from apps.accounts.models import User


class Todo(TimestampedModel):
    """
    Todo model with soft delete support.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='todos'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Todo'
        verbose_name_plural = 'Todos'

    def __str__(self):
        return self.title

    def soft_delete(self):
        """Soft delete the todo by setting is_active to False."""
        self.is_active = False
        self.save(update_fields=['is_active'])

    def restore(self):
        """Restore a soft-deleted todo."""
        self.is_active = True
        self.save(update_fields=['is_active'])
