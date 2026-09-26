from django.contrib import admin
from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    """
    TodoAdmin for managing Todo model in Django admin.
    Staff users can view and manage all todos across the system.
    """

    # Fields displayed in the todo list view
    list_display = [
        'title',
        'user',
        'is_completed',
        'created_at',
    ]

    # Fields that link to the detail view
    list_display_links = ['title']

    # Filters available in the right sidebar
    list_filter = [
        'is_completed',
        'created_at',
        'user',
    ]

    # Fields that can be searched
    search_fields = [
        'title',
        'description',
    ]

    # Ordering of the list view
    ordering = ['-created_at']

    # Number of items per page
    list_per_page = 25

    # Save buttons at the top of the form
    save_on_top = True

    # Show full count of results in filtered view
    show_full_result_count = True

    # Date hierarchy for navigation
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        """
        Override to allow staff users to see all todos.
        """
        qs = super().get_queryset(request)
        return qs.select_related('user')
