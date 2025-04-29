from django.utils.translation import gettext as _


# Status
UPLOADING = 1
COMPLETE = 2
CHUNKED_UPLOAD_CHOICES = (
    (UPLOADING, _('Uploading')),
    (COMPLETE, _('Complete')),
)

# MIME types
CONTENT_TYPE_FILE = 'application/octet-stream'
CONTENT_TYPE_TEXT = 'text/plain'
CONTENT_TYPE_JSON = 'application/json'

# Others
MAX_BYTES = 2 ** 31 - 1  # Max file size (usually 2GB)
COMPLETE_EXT = 'done'
INCOMPLETE_EXT = 'part'
FAILED_EXT = 'failed'

# HTTP responses
http_status = {
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    204: 'No Content',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    409: 'Conflict',
    415: 'Unsupported Media Type',
    500: 'Internal Server Error',
} 