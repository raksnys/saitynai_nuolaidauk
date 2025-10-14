from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        # Ensure OpenAPI extensions are imported so drf-spectacular can register them
        try:
            import users.helpers.openapi  # noqa: F401
        except Exception:
            # Avoid breaking startup if optional deps are missing; schema generation will warn instead
            pass
