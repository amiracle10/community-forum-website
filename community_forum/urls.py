"""
URL configuration for community_forum project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from website_community_forum import views
from website_community_forum.views import create_post, post_detail, delete_post


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('forum/<str:category>/', views.forum_category, name='forum_category'),
    path('discussions/', views.discussion_board, name= 'discussions'),
    path('events/', views.events_board, name= 'events'),
    path('topics/', views.topics_board, name= 'topics'),
    path('about/', views.about_board, name= 'about'),
    path('logout/', views.user_logout, name='logout'),
    path('login/', views.user_login, name='login'),
    path('api/posts/', create_post, name='create_post'),
    path('post/<int:post_id>/', post_detail, name='post_detail'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('simulate-online/', views.simulate_online_users),
    path('register/', views.register, name='register'),

]
