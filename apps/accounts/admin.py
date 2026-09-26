from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom UserAdmin for managing CustomUser model in Django admin.
    Provides full staff management capabilities with custom fieldsets,
    list display, filters, and search functionality.
    """

    # Fields displayed in the user list view
    list_display = [
        'email',
        'username',
        'is_active',
        'is_staff',
        'date_joined',
    ]

    # Fields that link to the detail view
    list_display_links = ['email', 'username']

    # Filters available in the right sidebar
    list_filter = [
        'is_active',
        'is_staff',
    ]

    # Fields that can be searched
    search_fields = [
        'email',
        'username',
        'first_name',
        'last_name',
    ]

    # Ordering of the list view
    ordering = ['-date_joined']

    # Fields displayed horizontally for many-to-many relationships
    filter_horizontal = ['groups', 'user_permissions']

    # Fieldsets for the change user form
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Fieldsets for the add user form
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'username',
                    'password1',
                    'password2',
                    'is_staff',
                    'is_active',
                ),
            },
        ),
    )

    # Fields that are read-only
    readonly_fields = ['last_login', 'date_joined']

    # Number of items per page
    list_per_page = 25

    # Save buttons at the top of the form
    save_on_top = True

    # Show full count of results in filtered view
    show_full_result_count = True
