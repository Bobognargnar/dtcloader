from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'

    def ready(self):
        # Import the receiver function here to ensure it's registered
        from common.signals import file_insert_validation,trigger_file_processing