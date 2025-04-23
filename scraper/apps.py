from django.apps import AppConfig


class ScraperConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scraper'

    def ready(self):
        # Importar o módulo de agendamento quando o app for carregado
        from . import scheduler
