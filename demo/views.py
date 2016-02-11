from django.views.generic.base import TemplateView, View
from django.shortcuts import get_object_or_404
from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView

from chunked_upload.response import Response
from chunked_upload.exceptions import ChunkedUploadError

import jwt
import json

from demo.models import MyChunkedUpload
from meta.models import Metadata
from django.http import HttpResponse
from token_auth.views import Refresh
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from chunked_upload_demo.settings import SECRET_KEY
import os


class ChunkedUploadDemo(TemplateView):
    template_name = 'chunked_upload_demo.html'


class ChunkedUploadView(ChunkedUploadView):

    model = MyChunkedUpload
    field_name = 'the_file'

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass


class ChunkedUploadedSize(View):

    def get(self, request):
        # Check if file exists
        # print "GET: SIZE"
        response = HttpResponse()
        print request.GET['file']

        upload_id = request.GET.get('uid')
        token = request.GET.get('token')
        try:
            print jwt.decode(token, SECRET_KEY)
        except:
            return Response('Authentication expired', status=401)

        print upload_id
        if upload_id != '':
            # queryset = MyChunkedUpload.objects.all()
            # chunked_uploaded = queryset.filter(upload_id=upload_id)
            chunked_uploaded = get_object_or_404(MyChunkedUpload,
                                                 upload_id=upload_id)
            print chunked_uploaded
            try:
                print chunked_uploaded.file
                print type(chunked_uploaded.file)
                print chunked_uploaded.file.open
                size = chunked_uploaded.file.size
                print 'SIZE is: ' + str(size)
                return Response({'size': size}, status=200)
            except IOError:
                return Response({'size': 0}, status=200)
        else:
            return Response({'size': 0}, status=200)

    def options(request):
        # print "OPTIONS: SIZE"
        response = HttpResponse()
        return Response({'size': 0}, status=200)

#
# class ChunkedUploadedLogin(View):
#
#     def get(request):
#         response = HttpResponse()
#         print request.GET
#         return response
#
#     def post(self, request, *args, **kwargs):
#         response = HttpResponse()
#         print request.body
#         return response


class SaveView(ChunkedUploadView):
    field_name = 'file'
    model = MyChunkedUpload

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        print "Everything fine..."
        pass

    def get_extra_attrs(self, request):
        """
        Extra attribute values to be passed to the new ChunkedUpload instance.
        Should return a dictionary-like object.
        """
        return {
            # 'offset': (int(request.POST['_chunkNumber']) + 1) *
            #            int(request.POST['_chunkSize'])
        }

    def create_chunked_upload(self, save=False, **attrs):
        """
        Creates new chunked upload instance. Called if no 'upload_id' is
        found in the POST data.
        """
        # print "create_chunked_upload..."
        chunked_upload = self.model(**attrs)
        # print chunked_upload
        # file starts empty
        chunked_upload.file.save(name='', content=ContentFile(''), save=save)
        return chunked_upload

    def options(self, request):
        # print "OPTIONS CHUNKS..."
        return Response({'size': 0}, status=200)

    def get_response_data(self, chunked_upload, request):
        """
        Data for the response. Should return a dictionary-like object.
        """
        token = request.POST.get('token')
        refresh = Refresh()
        new_payload = refresh.refresh(token)
        print new_payload
        # Refresh token
        return {
            'upload_id': chunked_upload.upload_id,
            'offset': chunked_upload.offset,
            'expires': chunked_upload.expires_on,
            'token': new_payload['token'],
            'user': new_payload['user']
        }

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests.
        """
        print "POST starts..."
        try:
            token = request.POST.get('token')
            try:
                print jwt.decode(token, SECRET_KEY)
                print "Everything fine..."
            except:
                return Response('Authentication expired', status=401)
            return self._post(request, *args, **kwargs)
            # return Response({}, status=200)
        except ChunkedUploadError as error:
            return Response(error.data, status=error.status_code)


class MyChunkedUploadCompleteView(ChunkedUploadCompleteView):

    model = MyChunkedUpload
    do_md5_check = True

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass

    def on_completion(self, uploaded_file, request):
        # Do something with the uploaded file. E.g.:
        # * Store the uploaded file on another model:
        # SomeModel.objects.create(user=request.user, file=uploaded_file)
        # * Pass it as an argument to a function:
        # function_that_process_file(uploaded_file)
        upload_id = request.POST.get('upload_id')
        metadata = json.loads(request.POST.get('meta'))
        meta_uid = metadata['meta_uid']
        chunked_upload = get_object_or_404(self.get_queryset(request),
                                           upload_id=upload_id)
        chunked_upload.meta_uid = meta_uid
        chunked_upload.save()
        #  Save Metadata
        metadata = json.loads(request.POST.get('meta'))
        print metadata
        meta_uid = metadata['meta_uid']
        print meta_uid
        token = request.POST.get('token')
        print token
        upload_id = request.POST.get('upload_id')
        print upload_id
        try:
            decoded = jwt.decode(token, SECRET_KEY)
        except:
            return Response('Authentication expired', status=404)

        user = User.objects.get(id=decoded['user_id'])
        print 'Vamos a probar...'
        meta = Metadata.objects.filter(uid=meta_uid)
        if len(meta) == 0:
            print 'PRIMERA VEZ!!!'
            meta = Metadata(
                user=user,
                uid=meta_uid,
                sequencing_platform=metadata['sequencing_platform'],
                sequencing_type=metadata['sequencing_type'],
                pre_assembled=metadata['pre_assembled'],
                isolation_source=metadata['isolation_source'],
                pathogenic=metadata['pathogenic'],
                sample_name=metadata['sample_name'],
                longitude=metadata['longitude'],
                latitude=metadata['latitude'],
                organism=metadata['organism'],
                strain=metadata['strain'],
                subtype=metadata['subtype'],
                country=metadata['country'],
                region=metadata['region'],
                city=metadata['city'],
                zip_code=metadata['zip_code'],
                location_note=metadata['location_note'],
                source_note=metadata['source_note'],
                pathogenicity_note=metadata['pathogenicity_note'],
                collected_by=metadata['collected_by'],
                email_address=metadata['email_address'],
                notes=metadata['notes'],
                collection_date=metadata['collection_date'],
                release_date=metadata['release_date'])
            try:
              meta.save()
            except:
              print 'Pues ha dado error...'
              meta = Metadata.objects.filter(uid=meta_uid)
              meta = meta[0]
        else:
            print 'YA EXISTIAAAAA'
            meta = meta[0]
            print meta
        print meta_uid
        files = MyChunkedUpload.objects.filter(meta_uid=meta_uid)
        print files
        for file in files:
            print meta
            file.meta_id = meta
            file.save()


    def get_response_data(self, chunked_upload, request):
        upload_id = request.POST.get('upload_id')
        uploaded = get_object_or_404(self.get_queryset(request),
                                           upload_id=upload_id)
        print uploaded
        print uploaded.meta_id
        return {'message': ("You successfully uploaded '%s' (%s bytes)!" %
                            (uploaded.filename, uploaded.offset)),
                'meta_id': uploaded.meta_id}

    def md5_check(self, chunked_upload, md5):
        """
        Verify if md5 checksum sent by client matches generated md5.
        """
        print chunked_upload.upload_id
        print '...........'
        print md5
        print '...........'
        print chunked_upload.md5
        print '...........'
        print chunked_upload.md5 == md5
        print '...........'
        if chunked_upload.md5 != md5:
            raise ChunkedUploadError(status=400,
                                     detail='md5 checksum does not match')

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests.
        """
        try:
            self.check_permissions(request)
            try:
                print jwt.decode(request.POST.get('token'), SECRET_KEY)
            except:
                return Response('Authentication expired', status=401)
            return self._post(request, *args, **kwargs)
        except ChunkedUploadError as error:
            return Response(error.data, status=error.status_code)
