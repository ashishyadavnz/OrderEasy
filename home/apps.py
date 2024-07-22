from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'
    verbose_name = "01. HOME"

    def ready(self):
        import home.signals
