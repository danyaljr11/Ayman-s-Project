from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        # Disable automatic creation of permissions
        from django.db.models.signals import post_migrate
        from django.contrib.auth.management import create_permissions
        post_migrate.disconnect(create_permissions, dispatch_uid="django.contrib.auth.management.create_permissions")
