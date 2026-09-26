from django.apps import AppConfig


class TodosConfig(AppConfig):
    """
    Configuration for the todos app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.todos'
    label = 'todos'

    def ready(self):
        pass
