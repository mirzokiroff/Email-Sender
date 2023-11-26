from rest_framework.views import APIView
from .tasks import send_to_gmail
from config import settings
from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from .tokens import get_tokens_for_user
from .oauth2 import oauth2_sign_in
from .serializers import UserSignUpSerializer, UserSignInSerializer, ProfileSerializer, EmailVerySerializer
from .models import User


class EmailSignUp(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EmailVerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.data.get('code')
        if code and (email := cache.get(f'{settings.CACHE_KEY_PREFIX}:{code}')):
            if user := cache.get(f'user:{email}'):
                cache.delete(f'{settings.CACHE_KEY_PREFIX}:{code}')
                cache.delete(f'user:{email}')
                user.save()
                return Response({"message": 'User is successfully activated'})
        return Response({"message": 'Code is expired or invalid'})


class UserAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        if User.objects.filter(email=data['email']).exists():
            raise ValueError("Email already is exists")
        user = User(**data)
        send_to_gmail.apply_async(args=[user.email], countdown=5)
        cache.set(f'user:{user.email}', user, timeout=settings.CACHE_TTL)
        return Response({"status": True, 'user': user.email}, status=201)


class UserSignInAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.data['email'])
        return Response({'status': True, 'email': serializer.data['email'], 'token': get_tokens_for_user(user)})

class Oauth2(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        if token:= data.get('token'):
            return Response(oauth2_sign_in(token))
        raise ValidationError('token is missing or invalid')

class ProfileView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, )
    parser_classes = [JSONParser]

    def get_object(self):
        return self.request.user