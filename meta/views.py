from django.shortcuts import render
from django.views.generic.base import View
import jwt
from chunked_upload_demo.settings import SECRET_KEY
from meta.models import Metadata
from django.contrib.auth.models import User
from django.core import serializers
from chunked_upload.response import Response
from demo.models import MyChunkedUpload
from django.http import StreamingHttpResponse, HttpResponse
from django.core.servers.basehttp import FileWrapper
import json


class SaveMeta(View):

    def post(self, request):
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
            meta.save()
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
        return Response('Everything went accordint to plan...', status=200)
        # print user
        # if meta_id is None:
        #     try:
        #         print 'getting UID'
        #         meta = Metadata.objects.get(uid=meta_uid)
        #         print meta
        #     except:
        #         print "FAILED: therefore it didnt exist"
        #         # Entry does not exits: Inser new meta
        #
        # else:
        #     # Meta already exists
        #     meta = Metadata.objects.get(id=meta_id)
        #
        # chunked_upload = get_object_or_404(self.get_queryset(request),
        #                                    upload_id=upload_id)
        # chunked_upload.meta_id = meta
        # chunked_upload.save()
        # except:
        #     print 'error'
        #     return Response('User not authenticated', status=404)

        # Rename file or move it somewhere else


class SendData(View):

    def get(self, request):
        token = request.GET['token']
        try:
            decoded = jwt.decode(token, SECRET_KEY)
        except:
            return Response('Authentication expired', status=404)
        all_meta = Metadata.objects.all()
        answer = []
        for meta in all_meta:
            entry = Metadata.objects.get(id=meta.id)
            data = serializers.serialize("json", [entry, ])
            struct = json.loads(data)[0]
            files = MyChunkedUpload.objects.filter(meta_id=meta.id)
            struct["fields"]["user"] = User.objects.get(id=meta.user_id).username
            struct["fields"]["n_files"] = len(files)
            struct["fields"]["files"] = [f.id for f in files]
            struct["fields"]["file_names"] = ' '.join([f.filename for f in files])
            answer.append(struct)
        # t = json.dumps([[obj for meta in ibj] for obj in answer])
        # print t
        # data = serializers.serialize("json", answer, fields=('files','n_files', 'user_id'))
        return Response(json.dumps(answer), mimetype='application/json')


class SendFile(View):

    def get(self, request):
        token = request.GET['token']
        file_id = request.GET['file_id']
        try:
            decoded = jwt.decode(token, SECRET_KEY)
        except:
            return Response('Authentication expired', status=404)
        fileUploaded = MyChunkedUpload.objects.get(id=file_id)
        fileToDownload = fileUploaded.get_uploaded_file()
        print fileUploaded.filename
        print fileUploaded.file.size
        response = StreamingHttpResponse(
            FileWrapper(fileToDownload, 1024*1024),
            content_type="application/octet-stream")
        response['Content-Disposition'] = 'attachment; filename="' + fileUploaded.filename + '"'
        response['Content-Length'] = fileUploaded.file.size
        return response
