
from django.contrib.auth.models import User
from oauth2_provider.models import AccessToken
from rest_framework.authtoken.models import Token
from rest_framework import generics
from api.permissions import IsAuthenticatedOrCreate
from api.serializers import (
    RegistrationSerializer, UserLoginSerializer, UserSerializer,
    ChangePasswordSerializer)
from oauth2_provider.ext.rest_framework import TokenHasScope
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.conf import settings

import json
import subprocess


class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = (IsAuthenticatedOrCreate,)


class UserActivation(generics.UpdateAPIView):

    def get(self, request, token, user_id, format=None):
        user_obj = User.objects.get(id=user_id)
        token_obj = Token.objects.get(user_id=user_obj)
        if user_obj.is_active == 0:
            if token_obj:
                key = token_obj.key
                if key == token:
                    user_obj.is_active = 1
                    user_obj.save(update_fields=['is_active'])
            serializer = RegistrationSerializer(user_obj)
            serialized_user = serializer.data
            serialized_user['message'] = 'your registration has been activated'
            return HttpResponse(json.dumps(serialized_user), content_type="application/json")
        else:
            serializer = RegistrationSerializer(user_obj)
            serialized_user = serializer.data
            serialized_user['message'] = 'Activation already Done'
            return HttpResponse(json.dumps(serialized_user), content_type="application/json")


class UserAPILoginView (APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request, * args, ** kwargs):
        data = request.data
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            new_data = serializer.data
            cmd = 'curl -X POST -d "grant_type=password&username=%s&password=%s" -u "%s:%s" localhost:8000/o/token/' % (
                data['email'], data['password'], settings.CLIENT_ID, settings.CLIENT_SECRET)
            subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            resp = subprocess.check_output(['bash', '-c', cmd])
            resp = json.loads(resp)
            new_data['access_token'] = resp['access_token']
            new_data['token_type'] = resp['token_type']
            new_data['expires_in'] = resp['expires_in']
            new_data['refresh_token'] = resp['refresh_token']
            new_data['scope'] = resp['scope']
            return Response(new_data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    required_scopes = ['read']
    serializer_class = UserSerializer
    permission_classes = [TokenHasScope]


class ChangePassword(generics.UpdateAPIView):
    """ Change password API """
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            newpassword = request.data['newpassword']
            access_token = request.data['token']
            confirm_password = request.data['confirm_password']

            if newpassword != confirm_password:
                return Response({"confirm_password": ["Password not matches."]})

            token = AccessToken.objects.get(token=access_token)
            user_id = token.user_id
            user_detail = User.objects.get(id=user_id)

            if not user_detail.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]})

            # set_password also hashes the password that the user will get
            user_detail.set_password(serializer.data.get("newpassword"))
            user_detail.save()
            return Response("Success.")
        else:
            return Response(
                "There is some fileds are missing, please try again!")
