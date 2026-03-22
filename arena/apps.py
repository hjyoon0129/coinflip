from django.apps import AppConfig


class ArenaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "arena"

    def ready(self):
        import arena.signals