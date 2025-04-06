from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ResetPasswordView
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),

    path('refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<int:user_id>/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),

    path('follow/<int:user_id>/', views.toggle_follow, name='toggle_follow'),
]
