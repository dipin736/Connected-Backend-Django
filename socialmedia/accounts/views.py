from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from .models import CustomUser
from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer, UserSignupSerializer, UserLoginSerializer
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .models import Friendship

# Signup View
@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login View
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class ForgotPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        # Validate the email input
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # Check if the user exists
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({"detail": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate the password reset token
            token = default_token_generator.make_token(user)
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{user.id}/{token}/"  # Adjust frontend URL accordingly

            # Send the reset link via email
            send_mail(
                'Password Reset Request',
                f'Click the following link to reset your password: {reset_link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            
            return Response({"detail": "Password reset link sent to email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ResetPasswordView(APIView):
    def post(self, request, user_id, token, *args, **kwargs):
        # Validate the token
        try:
            user = get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            return Response({"detail": "User not found."}, status=400)

        # Check token validity
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=400)

        # Validate new password
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Password reset successfully."}, status=200)
        return Response(serializer.errors, status=400)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_follow(request, user_id):
    try:
        target_user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'detail': 'User not found'}, status=404)

    current_user = request.user

    if target_user == current_user:
        return Response({'detail': "You can't follow yourself"}, status=400)

    if Friendship.objects.filter(from_user=current_user, to_user=target_user).exists():
        # Unfollow
        Friendship.objects.filter(from_user=current_user, to_user=target_user).delete()
        action = "unfollowed"
    else:
        # Follow
        Friendship.objects.create(from_user=current_user, to_user=target_user)
        action = "followed"

    return Response({
        'status': action,
        'friends_count': target_user.friends.count()
    })
