from django.urls import path
from .views import UserSignInAPIView, Oauth2, ProfileView, UserAPIView, EmailSignUp


urlpatterns = [
    path('sign-up', UserAPIView.as_view(), name="sign-up"),
    path('sign-in', UserSignInAPIView.as_view(), name="sign-in"),
    path('oauth2', Oauth2.as_view(), name="oauth2"),
    path('profile', ProfileView.as_view(), name="profile"),
    path('email-verify', EmailSignUp.as_view(), name="email-verify")
]
