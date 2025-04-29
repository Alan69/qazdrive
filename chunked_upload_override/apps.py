from django.apps import AppConfig


class ChunkedUploadOverrideConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chunked_upload_override' 