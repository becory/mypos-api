import os

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from jwt import decode as jwt_decode
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.state import User
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import User as django_user


class POSTokenVerifySerializer(TokenVerifySerializer):
    token = serializers.CharField()

    def validate(self, attrs):
        app = os.environ.get('DJANGO_SETTINGS_MODULE').split('.')
        UntypedToken(attrs['token'])
        data = jwt_decode(attrs['token'], globals()[app[0]][app[1]].SECRET_KEY,
                          algorithms=['HS256'])
        user_id = data[api_settings.USER_ID_CLAIM]
        if data['token_type']:
            user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})

            data = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }

            if user.is_superuser:
                data['roles'] = ['admin']
            elif user.is_staff:
                data['roles'] = ['editor']

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = django_user
        fields = ('username', 'first_name', 'last_name', 'email', 'is_superuser', 'is_staff')


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = django_user
        fields = ('first_name', 'last_name', 'email', 'password', 'username', 'is_staff', 'is_superuser')

    def create(self, validated_data):
        user = super(UserCreateSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
