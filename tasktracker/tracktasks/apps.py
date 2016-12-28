from django.apps import AppConfig


class TracktasksConfig(AppConfig):
    name = 'tracktasks'

    def ready(self):
        import tracktasks.signals
