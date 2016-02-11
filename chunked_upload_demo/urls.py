from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin

from demo.views import (
    ChunkedUploadDemo, MyChunkedUploadCompleteView,
    SaveView, ChunkedUploadedSize
)

from meta.views import SendData, SendFile, SaveMeta
from token_auth.views import Refresh

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^/?$',
        ChunkedUploadDemo.as_view(), name='chunked_upload'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^login/', 'jwt_auth.views.obtain_jwt_token'),
    url(r'^token/refresh/', Refresh.as_view(), name='refres_token'),
    url(r'^api/save/?$',
        MyChunkedUploadCompleteView.as_view(),
        name='api_chunked_upload_complete'),
    url(r'^api/chunks/?$', SaveView.as_view(),
        name='api_chunked_upload_save'),
    url(r'^api/size/?$', ChunkedUploadedSize.as_view(),
        name='api_chunked_upload_size'),

    url(r'^api/data/?$', SendData.as_view(),
        name='api_chunked_upload_data'),
    url(r'^api/meta/save/?$', SaveMeta.as_view(),
        name='api_chunked_upload_data'),
    url(r'^api/file/?$', SendFile.as_view(),
        name='api_chunked_upload_data'),

    url(r'^static/(.*)$',
        'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': False}),
)
