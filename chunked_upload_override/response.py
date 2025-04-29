import json
from django.http import HttpResponse

from .settings import CONTENT_TYPE, ENCODER, MIMETYPE


class Response(HttpResponse):
    """
    A custom response object for handling file uploads.
    """

    def __init__(self, data='', *args, **kwargs):
        # Set content_type
        kwargs.setdefault('content_type', CONTENT_TYPE)
        
        # Handle data
        if not isinstance(data, str):
            data = ENCODER(data)
            
        super(Response, self).__init__(data, *args, **kwargs) 