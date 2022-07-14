from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import parser_classes
from app.models import Account

from app.serializers import UserSerializer, UserSerializerWithToken
# Create your views here.
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.hashers import make_password
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

# verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from decouple import config

# verification email
from django.core.mail import EmailMessage


User = get_user_model()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
def checkUser(request):
    data = request.data
    email = data['email']
    if (Account.objects.filter(email=email).exists()):
        message = {'detail': 'User exists'}
        return Response(message, status=status.HTTP_200_OK)

    else:
        message = {'detail': 'User does not exist'}
        return Response(message, status=status.HTTP_200_OK)


@api_view(['GET'])
def UsersCount(request):
    try:
        count = Account.objects.count()
        message = {'total': count}
        return Response(message, status=status.HTTP_200_OK)

    except:
        message = {'detail': 'could not perform count'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@parser_classes((MultiPartParser, ))
def registerUser(request):
    data = request.data
    profile_picture = request.FILES.get('profile_picture')
    email = data['email']

    try:
        user = User.objects.create_user(
            full_name=data['name'],
            email=data['email'],
            phone_number=data['phone'],
            country=data['country'],
            password=data['password']
        )

        user.profile_picture = profile_picture
        user.save()

        # Successful registration email sending
        current_site = settings.REACT_APP_URL
        subject = 'Registration success'
        message = render_to_string('account/register_thankyou_email.html', {
            'user': user,
            'domain': current_site,
            'protocol': 'http'
        })

        # Launch asynchronous task
        register_mail.delay(subject, message, email)

        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data)
    except:
        message = {'detail': 'User with this email already exists'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@parser_classes((MultiPartParser, ))
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = get_object_or_404(Account, id=request.user.id)
    data = request.data
    profile_picture = request.FILES.get('profile_picture')

    for key, value in data.lists():
        if key == "profile_picture":
            if profile_picture:
                user.profile_picture = profile_picture
            else:
                pass
        else:
            name = data.get(key)
            if name == "":
                pass
            else:
                setattr(user, key, name)

    user.save()
    serializer = UserSerializerWithToken(user)

    return Response(data=serializer.data, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUserById(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUser(request, pk):
    user = User.objects.get(id=pk)
    data = request.data

    user.first_name = data['name']
    user.email = data['email']
    user.is_staff = data['isAdmin']

    user.save()

    serializer = UserSerializer(user, many=False)

    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteUser(request, pk):
    userForDeletion = User.objects.get(id=pk)
    userForDeletion.delete()
    return Response('User was deleted')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def changePassword(request):
    data = request.data
    current_password = data['current_password']
    new_password = data['new_password']
    confirm_password = data['confirm_password']

    user = get_object_or_404(Account, id=request.user.id)

    if new_password == confirm_password:
        success = user.check_password(current_password)
        if success:
            user.set_password(new_password)
            user.save()

            message = {
                'detail': 'Password updated successfully. You can login with new password.'}
            return Response(data=message, status=status.HTTP_205_RESET_CONTENT)

        else:
            message = {'detail': 'Enter a valid current password.'}
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Your passwords do not match.'}
        return Response(data=message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def forgotPassword(request):
    data = request.data
    email = data['email']
    if Account.objects.filter(email=email).exists():
        user = Account.objects.get(email__exact=email)

        # reset password email sending
        current_site = settings.REACT_APP_URL
        subject = 'Reset your password'
        message = render_to_string('account/reset_password_email.html', {
            'user': user,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'protocol': 'http'
        })

        # Launch asynchronous task
        resetpassword_mail.delay(subject, message, email)

        message = {'detail': 'Password reset link has been sent to your email'}
        return Response(data=message, status=status.HTTP_200_OK)

    else:
        message = {'detail': 'User does not exist'}
        return Response(data=message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def resetPassword(request):
    data = request.data
    password = data['password']
    confirm_password = data['confirm_password']
    uidb64 = data['uid']
    token = data['token']

    if password == confirm_password:
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account._default_manager.get(id=uid)

        except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(password)
            user.save()
            serializer = UserSerializerWithToken(user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        else:
            message = {'detail': 'Sorry, this link may be expired.'}
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Passwords do not match'}
        return Response(data=message, status=status.HTTP_400_BAD_REQUEST)
