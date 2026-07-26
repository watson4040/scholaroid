from django.apps import AppConfig


class SettingsappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "settingsApp"
    verbose_name = "School Settings"

    def ready(self):
        try:
            import settingsApp.signals
        except ImportError:
            pass