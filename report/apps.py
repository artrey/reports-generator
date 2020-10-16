from django.apps import AppConfig


class ReportConfig(AppConfig):
    name = 'report'

    def ready(self):
        # register post actions
        from . import post_actions
