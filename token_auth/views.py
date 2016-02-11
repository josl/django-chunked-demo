from django.views.generic.base import View
from jwt_auth import settings
from django import forms
import jwt
from jwt_auth.compat import json, smart_text
from chunked_upload_demo.settings import SECRET_KEY
from django.contrib.auth.models import User
from calendar import timegm
from datetime import datetime, timedelta
from chunked_upload.response import Response

jwt_payload_handler = settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = settings.JWT_ENCODE_HANDLER
jwt_decode_handler = settings.JWT_DECODE_HANDLER
jwt_get_user_id_from_payload = settings.JWT_PAYLOAD_GET_USER_ID_HANDLER


# Create your views here.
class Refresh(View):
    def _check_payload(self, token):
        # Check payload valid (based off of JSONWebTokenAuthentication,
        # may want to refactor)
        try:
            print token
            print SECRET_KEY
            payload = jwt.decode(token, SECRET_KEY)
            print payload
        except jwt.ExpiredSignature:
            msg = 'Signature has expired'
            raise forms.ValidationError(msg)
        except jwt.DecodeError:
            msg = 'Error decoding signature'
            raise forms.ValidationError(msg)

        return payload

    def _check_user(self, payload):
        username = payload.get('username')

        if not username:
            msg = 'Invalid payload'
            raise forms.ValidationError(msg)

        # Make sure user exists
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            msg = 'User doesn\'t exist.'
            raise forms.ValidationError(msg)

        if not user.is_active:
            msg = 'User account is disabled'
            raise forms.ValidationError(msg)

        return user

    def refresh(self, token):

        payload = self._check_payload(token=token)
        user = self._check_user(payload=payload)
        print 'lalla'
        print user
        # Get and check 'orig_iat'
        orig_iat = payload.get('orig_iat')
        print orig_iat
        if orig_iat:
            # Verify expiration
            refresh_limit = settings.JWT_REFRESH_EXPIRATION_DELTA
            print refresh_limit
            if isinstance(refresh_limit, timedelta):
                refresh_limit = (refresh_limit.days * 24 * 3600 +
                                 refresh_limit.seconds)

            expiration_timestamp = orig_iat + int(refresh_limit)
            now_timestamp = timegm(datetime.utcnow().utctimetuple())
            print now_timestamp
            if now_timestamp > expiration_timestamp:
                msg = 'Refresh has expired'
                raise forms.ValidationError(msg)
        else:
            msg = 'orig_iat field is required'
            raise forms.ValidationError(msg)

        new_payload = {
            'user_id': user.pk,
            'email': user.email,
            'username': user.username,
            'exp': datetime.utcnow() + settings.JWT_EXPIRATION_DELTA
        }
        print new_payload

        if settings.JWT_ALLOW_REFRESH:
            new_payload['orig_iat'] = timegm(
                datetime.utcnow().utctimetuple()
            )
        new_payload['orig_iat'] = orig_iat

        return {
            'token': jwt.encode(new_payload, SECRET_KEY),
            'user': user.username
        }

    def post(self, request):
        request_json = json.loads(smart_text(request.body))
        print request_json
        token = request_json['token']
        new_payload = self.refresh(token)
        return Response(json.dumps(new_payload), mimetype='application/json')
