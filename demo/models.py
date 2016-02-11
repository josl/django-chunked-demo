from chunked_upload.models import ChunkedUpload
from django.db import models
from meta.models import Metadata


class MyChunkedUpload(ChunkedUpload):
    meta = models.ForeignKey(Metadata, on_delete=models.CASCADE, null=True)
    meta_uid = models.CharField(max_length=32, editable=False)

# Override the default ChunkedUpload to make the `user` field nullable
MyChunkedUpload._meta.get_field('user').null = True
