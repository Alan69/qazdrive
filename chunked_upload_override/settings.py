import datetime
import time

from django.conf import settings

try:
    from django.core.serializers.json import DjangoJSONEncoder
except ImportError:
    try:
        # Deprecated class name (for backwards compatibility purposes)
        from django.core.serializers.json import (
            DateTimeAwareJSONEncoder as DjangoJSONEncoder
        )
    except ImportError:
        raise ImportError('Error importing JSONEncoder class')


# How long after creation the upload will expire
DEFAULT_EXPIRATION_DELTA = datetime.timedelta(days=1)
EXPIRATION_DELTA = getattr(settings, 'CHUNKED_UPLOAD_EXPIRATION_DELTA',
                           DEFAULT_EXPIRATION_DELTA)


# Path where uploading files will be stored until completion
DEFAULT_UPLOAD_PATH = 'chunked_uploads/%Y/%m/%d'
UPLOAD_PATH = getattr(settings, 'CHUNKED_UPLOAD_PATH', DEFAULT_UPLOAD_PATH)


# Storage system
STORAGE = getattr(settings, 'CHUNKED_UPLOAD_STORAGE_CLASS', lambda: None)()

if STORAGE is None:  # If no storage was provided, use the default storage system
    from django.core.files.storage import default_storage
    STORAGE = default_storage


# Function used to encode response data. Receives a dict and returns a string
DEFAULT_ENCODER = DjangoJSONEncoder().encode
ENCODER = getattr(settings, 'CHUNKED_UPLOAD_ENCODER', DEFAULT_ENCODER)


# Content-Type for the response data
DEFAULT_CONTENT_TYPE = 'application/json'
CONTENT_TYPE = getattr(settings, 'CHUNKED_UPLOAD_CONTENT_TYPE',
                       DEFAULT_CONTENT_TYPE)


# Max amount of data (in bytes) that can be uploaded per request
DEFAULT_MAX_BYTES = 4 * 1024 * 1024  # 4 MB
MAX_BYTES = getattr(settings, 'CHUNKED_UPLOAD_MAX_BYTES', DEFAULT_MAX_BYTES)


# Mimetype for the response data
DEFAULT_MIMETYPE = 'application/json'
MIMETYPE = getattr(settings, 'CHUNKED_UPLOAD_MIMETYPE', DEFAULT_MIMETYPE)  # For the old version of Django


# Name of the cookie/session parameter that contain the auth token
DEFAULT_AUTH_COOKIE_NAME = 'sessionid'
AUTH_COOKIE_NAME = getattr(settings, 'CHUNKED_UPLOAD_AUTH_COOKIE_NAME', DEFAULT_AUTH_COOKIE_NAME)


# Custom upload model, if any. 
DEFAULT_MODEL = 'chunked_upload.models.ChunkedUpload'
MODEL = getattr(settings, 'CHUNKED_UPLOAD_MODEL', DEFAULT_MODEL)


DEFAULT_COMPLETE_UPLOAD = 2
COMPLETE_UPLOAD = getattr(settings, 'CHUNKED_UPLOAD_COMPLETE_STATUS', DEFAULT_COMPLETE_UPLOAD)


# Boolean that defines if the ChunkedUpload model is abstract or not
DEFAULT_ABSTRACT_MODEL = True
ABSTRACT_MODEL = getattr(settings, 'CHUNKED_UPLOAD_ABSTRACT_MODEL',
                         DEFAULT_ABSTRACT_MODEL) 