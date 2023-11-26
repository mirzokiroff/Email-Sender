from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.fields import CharField, EmailField
from .models import User


class EmailVerySerializer(Serializer):
    code = CharField(max_length=5)


class UserSignUpSerializer(Serializer):
    email = EmailField(max_length=128)
    password = CharField(min_length=8, max_length=128)
    confirm_password = CharField(min_length=8, max_length=255, write_only=True)

    def validate(self, attrs):
        password = attrs.pop('password')
        confirm_password = attrs.pop('confirm_password')
        if password and confirm_password and password == confirm_password:
            attrs['password'] = make_password(password)
            return attrs
        raise ValueError('Password error!')


class UserSignInSerializer(Serializer):
    email = EmailField(max_length=255)
    password = CharField(min_length=8, max_length=255)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            return attrs
        raise ValueError('Invalid Password or Email')

class ProfileSerializer(ModelSerializer):
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = "first_name", "last_name", "email", "password"
