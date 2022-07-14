from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email',
                  'phone_number', 'country', 'is_admin', 'token']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)


class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'phone_number', 'country',
                  'is_active', 'is_admin', 'date_joined', 'token', 'profile_picture']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)
