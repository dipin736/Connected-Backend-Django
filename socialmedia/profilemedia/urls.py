from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.update_user_profile, name='profile'),
    path('profile/<int:user_id>/', views.get_user_profile, name='get-user-profile'),

    path('get_all_users/', views.get_all_users, name='get_all_users'),

    path('profile/<int:user_id>/friends/', views.get_user_friends, name='get_user_friends'),

    path('posts/create/', views.create_post, name='create_post'),


    path('posts/user/<int:user_id>/', views.get_user_posts, name='get_user_posts'),

    path('posts/<int:post_id>/', views.delete_post, name='delete_post'),

    path('get_all_posts/', views.get_all_posts, name='get_all_posts'),

    path('posts/<int:post_id>/like/', views.like_post, name='like_post'),
    path('posts/<int:post_id>/comment/', views.comment_post, name='comment_post'),
    path('posts/<int:post_id>/is_liked/', views.is_liked, name='is_liked'),
    path('posts/<int:post_id>/like_count/', views.get_like_count, name='get_like_count'),



    path('posts/<int:post_id>/comment_count/', views.get_comment_count, name='get_comment_count'),
      
    path('posts/<int:post_id>/comments/', views.get_comments, name='get_comments'),

    path('create_story/', views.create_story, name='create_story'),

    path('get_stories/', views.get_stories, name='get_stories'),

     path('history/<int:user1>/<int:user2>/', views.ChatHistoryView.as_view(), name='chat-history'),

     path('online-users/', views.get_online_users, name='online-users'),


]
