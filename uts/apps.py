from django.apps import AppConfig


class UtsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'uts'

    def ready(self):
        super().ready()
        import uts.signals
        uts.signals.ready = True
