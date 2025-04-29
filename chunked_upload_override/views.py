import re
import json
from email.generator import _make_boundary as make_boundary

from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from .settings import MAX_BYTES
from .models import ChunkedUpload
from .response import Response
from .constants import http_status


class ChunkedUploadView(View):
    """
    Base view for chunked uploads. Inherit from this to provide your own functionality.
    """
    model = ChunkedUpload
    field_name = None  # set to 'file' by default
    content_range_header = 'HTTP_CONTENT_RANGE'
    content_range_pattern = re.compile(r'^bytes (\d+)-(\d+)/(\d+)$')
    max_bytes = MAX_BYTES  # Max amount of data that can be uploaded
    response_class = Response

    def get_queryset(self, request):
        """
        Get (and filter) ChunkedUpload queryset.
        By default, users can only continue uploading their own uploads.
        """
        queryset = self.model.objects.all()
        if hasattr(request, 'user') and request.user.is_authenticated:
            queryset = queryset.filter(user=request.user)
        return queryset

    def validate(self, request):
        """
        Placeholder method to define extra validation.
        Must raise an error if validation fails.
        """
        pass

    def get_response_data(self, chunked_upload, request):
        """
        Data for the response. Should return a dictionary or a list.
        Called *only* if POST is successful.
        """
        return {
            'upload_id': chunked_upload.upload_id.hex,
            'offset': chunked_upload.offset,
            'expires': chunked_upload.expires_at
        }

    def _save_chunked_upload(self, chunked_upload):
        """
        Placeholder method to define how to save the upload.
        """
        chunked_upload.save()

    def _get_content_range(self, request):
        """
        Gets the Content-Range header.
        """
        content_range = request.META.get(self.content_range_header, '')
        match = self.content_range_pattern.match(content_range)
        return match

    def _get_chunked_upload(self, request, upload_id=None):
        field_name = self.field_name or request.POST.get('field_name', 'file')
        chunked_upload = None
        if upload_id:
            try:
                chunked_upload = get_object_or_404(
                    self.get_queryset(request), upload_id=upload_id
                )
            except:
                pass

        return chunked_upload, field_name

    def check_permissions(self, request):
        """
        Grants permission to start/continue an upload based on the request.
        """
        if hasattr(request, 'user') and not request.user.is_authenticated:
            raise self.PermissionDenied("Authentication required to upload files")

    def handle_upload(self, request):
        """
        Handle the upload request.
        """
        self.check_permissions(request)
        self.validate(request)

        content_range = self._get_content_range(request)
        retry = False

        if content_range is None:
            # First request, so start a new upload
            chunked_upload, field_name = self._get_chunked_upload(request)

            if chunked_upload is None:
                # First request, create a new chunked upload
                chunked_upload = self.model()
                if hasattr(request, 'user') and request.user.is_authenticated:
                    chunked_upload.user = request.user

            # File attributes for the model
            try:
                uploaded_file = request.FILES[field_name]
            except KeyError:
                uploaded_file = None
            except:
                raise self.ChunkedUploadError(
                    status=http_status[400],
                    detail='No file found'
                )

            if not uploaded_file:
                raise self.ChunkedUploadError(
                    status=http_status[400],
                    detail='No file found'
                )

            chunked_upload.filename = uploaded_file.name
            chunked_upload.offset = 0

            try:
                # Initialize the chunked upload
                chunked_upload.file.save(uploaded_file.name, ContentFile(''))
                chunked_upload.append_chunk(uploaded_file, save=False)
            except:
                # Remove file and rethrow
                chunked_upload.delete()
                raise

            # Save the chunked upload
            self._save_chunked_upload(chunked_upload)
        else:
            # Get upload id from request
            upload_id = request.POST.get('upload_id')

            # Get existing upload
            chunked_upload, field_name = self._get_chunked_upload(request, upload_id)

            if chunked_upload is None:
                raise self.ChunkedUploadError(
                    status=http_status[404],
                    detail='Upload not found'
                )

            try:
                uploaded_file = request.FILES[field_name]
            except KeyError:
                uploaded_file = None
            except:
                raise self.ChunkedUploadError(
                    status=http_status[400],
                    detail='No file found'
                )

            if not uploaded_file:
                raise self.ChunkedUploadError(
                    status=http_status[400],
                    detail='No file found'
                )

            # Check if correct chunk was sent
            start_bytes = int(content_range.group(1))
            end_bytes = int(content_range.group(2))
            total_bytes = int(content_range.group(3))

            # Check for data corruption
            if chunked_upload.offset != start_bytes:
                # Chunk mismatch, try reupload
                retry = True
            else:
                # Check if the user has enough space
                if end_bytes >= total_bytes:
                    raise self.ChunkedUploadError(
                        status=http_status[400],
                        detail='End bytes cannot exceed total bytes'
                    )

                try:
                    chunked_upload.append_chunk(uploaded_file, save=False)
                except:
                    # Remove file & rethrow
                    chunked_upload.delete()
                    raise

                # Save the chunked upload
                self._save_chunked_upload(chunked_upload)

        # Get response data
        data = self.get_response_data(chunked_upload, request)
        if retry:
            # Include retry flag in the response
            data['retry'] = True
            data['upload_id'] = chunked_upload.upload_id.hex
            data['offset'] = chunked_upload.offset

        # Return a JSON response with data
        return JsonResponse(data)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ChunkedUploadView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests.
        """
        try:
            return self.handle_upload(request)
        except self.ChunkedUploadError as error:
            return Response(error.data, status=error.status)
        except Exception as error:
            return Response(str(error), status=http_status[500])

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests.
        """
        raise NotImplementedError

    class PermissionDenied(Exception):
        """
        Exception raised when a request fails the permission check.
        """
        pass

    class ChunkedUploadError(Exception):
        """
        Exception raised when an error occurs during chunked upload.
        """

        def __init__(self, status=http_status[500], detail=None):
            self.status = status
            self.data = {
                'error': detail or 'Error uploading file'
            }


class ChunkedUploadCompleteView(View):
    """
    Base view for completion of chunked upload.
    """
    model = ChunkedUpload
    do_md5_check = False
    response_class = Response

    def get_queryset(self, request):
        """
        Get (and filter) ChunkedUpload queryset.
        By default, users can only complete their own uploads.
        """
        queryset = self.model.objects.all()
        if hasattr(request, 'user') and request.user.is_authenticated:
            queryset = queryset.filter(user=request.user)
        return queryset

    def validate(self, request):
        """
        Placeholder method to define extra validation.
        Must raise an error if validation fails.
        """
        pass

    def on_completion(self, chunked_upload, request):
        """
        Placeholder method to define what to do when upload is complete.
        """
        pass

    def get_response_data(self, chunked_upload, request):
        """
        Data for the response. Should return a dictionary or a list.
        Called *only* if POST is successful.
        """
        return {'message': 'Upload complete'}

    def check_permissions(self, request):
        """
        Grants permission to complete upload based on the request.
        """
        if hasattr(request, 'user') and not request.user.is_authenticated:
            raise self.PermissionDenied("Authentication required to upload files")

    def _get_chunked_upload(self, request, upload_id=None):
        """
        Tries to get the chunked upload with the specified upload_id.
        """
        upload_id = upload_id or request.POST.get('upload_id')

        if not upload_id:
            raise self.ChunkedUploadError(
                status=http_status[400],
                detail='Upload ID is required'
            )

        try:
            return get_object_or_404(
                self.get_queryset(request), upload_id=upload_id
            )
        except:
            raise self.ChunkedUploadError(
                status=http_status[404],
                detail='Upload not found'
            )

    def _md5_check(self, chunked_upload, md5):
        """
        Verifies that the md5 checksum sent by the client matches the generated one.
        """
        if chunked_upload.md5 != md5:
            chunked_upload.close_file()
            raise self.ChunkedUploadError(
                status=http_status[400],
                detail='MD5 checksum does not match'
            )
        return True

    def handle_completed_upload(self, request):
        """
        Handle a completed upload request.
        """
        self.check_permissions(request)
        self.validate(request)

        chunked_upload = self._get_chunked_upload(request)

        md5 = request.POST.get('md5')
        if self.do_md5_check and md5:
            self._md5_check(chunked_upload, md5)

        chunked_upload.completed()

        self.on_completion(chunked_upload, request)
        return self.get_response_data(chunked_upload, request)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ChunkedUploadCompleteView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests.
        """
        try:
            response = self.handle_completed_upload(request)
            return JsonResponse(response)
        except self.ChunkedUploadError as error:
            return Response(error.data, status=error.status)
        except Exception as error:
            return Response(str(error), status=http_status[500])

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests.
        """
        raise NotImplementedError

    class PermissionDenied(Exception):
        """
        Exception raised when a request fails the permission check.
        """
        pass

    class ChunkedUploadError(Exception):
        """
        Exception raised when an error occurs during chunked upload.
        """

        def __init__(self, status=http_status[500], detail=None):
            self.status = status
            self.data = {
                'error': detail or 'Error uploading file'
            } 