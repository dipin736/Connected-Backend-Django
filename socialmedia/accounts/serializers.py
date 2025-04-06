from django.contrib.auth import get_user_model
from django.forms import ValidationError
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import password_validation
from rest_framework_simplejwt.tokens import RefreshToken

class UserSignupSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['fullname', 'username', 'email', 'password']

    def create(self, validated_data):
        # ✅ Use DRF's ValidationError for JSON response
        if get_user_model().objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError({"email": ["This email is already in use."]})

        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['fullname'],
        )
        return user



class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        refresh = RefreshToken.for_user(user)
        refresh.payload['username'] = user.username
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
