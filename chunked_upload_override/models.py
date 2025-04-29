import hashlib
import uuid
import os
import datetime
import re

from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext as _

from .settings import (
    EXPIRATION_DELTA,
    UPLOAD_PATH,
    STORAGE,
    ABSTRACT_MODEL,
    COMPLETE_UPLOAD
)
from .constants import CHUNKED_UPLOAD_CHOICES, UPLOADING


class ChunkedUpload(models.Model):
    """
    Base chunked upload model. This model is abstract, and must be
    subclassed using the 'inherit' argument. Use the helper in managers.py to
    create a concrete subclass of this model with the correct options.
    """
    upload_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    file = models.FileField(max_length=255, upload_to=UPLOAD_PATH, storage=STORAGE)
    filename = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chunked_uploads',
                          on_delete=models.CASCADE, null=True)
    offset = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(choices=CHUNKED_UPLOAD_CHOICES, default=UPLOADING)
    completed_at = models.DateTimeField(null=True, blank=True)

    @property
    def expires_at(self):
        """
        Returns the expiration time.
        """
        return self.created_at + EXPIRATION_DELTA

    @property
    def expired(self):
        """
        Returns whether this upload has expired or not.
        """
        return now() > self.expires_at

    @property
    def md5(self, rehash=False):
        """
        Returns the MD5 hash of the file.
        If rehash is True, then also recomputes the hash.
        Otherwise, returns the hash stored in the database.
        """
        if rehash:
            self.file.close()
            md5 = hashlib.md5()
            self.file.open(mode='rb')
            for chunk in self.file.chunks():
                md5.update(chunk)
            self.file.close()
            return md5.hexdigest()
        else:
            if re.match(r'^[a-f0-9]{32}$', self.filename):
                return self.filename
            else:
                return None

    def delete(self, delete_file=True, *args, **kwargs):
        if self.file:
            storage, path = self.file.storage, self.file.path
        super(ChunkedUpload, self).delete(*args, **kwargs)
        if self.file and delete_file:
            storage.delete(path)

    def __str__(self):
        return u'<%s - upload_id: %s - bytes: %s - status: %s>' % (
            self.filename, self.upload_id, self.offset, self.status)

    def close_file(self):
        """
        Bug in django 1.4: FieldFile.close() does not actually close the file
        if it's already open. So we need to explicitly close it.
        """
        if self.file:
            self.file.close()

    def append_chunk(self, chunk, chunk_size=None, save=True):
        """
        Appends the given data to the file. If the provided size did not match,
        returns False.
        """
        self.close_file()
        self.file.open(mode='ab')  # mode = append+binary
        # We can use .read() safely because chunk is already in memory
        self.file.write(chunk.read())
        if chunk_size and chunk.size != chunk_size:
            self.file.close()
            return False
        self.offset += chunk.size
        self.file.close()
        if save:
            self.save()
        return True

    def get_uploaded_file(self):
        """
        Returns an UploadedFile instance from the file of this model.
        """
        self.close_file()
        self.file.open(mode='rb')  # mode = read+binary
        return UploadedFile(
            file=self.file, name=self.filename,
            content_type='application/octet-stream',
            size=self.offset
        )

    def completed(self, completed_at=None):
        """
        Marks the upload as completed and optionally sets the completed_at time.
        Returns True if the upload was successfully marked as completed, False
        if it was already complete or failed.
        """
        if self.status == UPLOADING:
            if completed_at is None:
                completed_at = now()
            self.status = COMPLETE_UPLOAD
            self.completed_at = completed_at
            self.save()
            return True
        return False

    class Meta:
        abstract = ABSTRACT_MODEL 