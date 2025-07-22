from django.urls import path
from . import views

urlpatterns = [
    path('admin-page/', views.admin_view, name='admin'),
    path('chat/', views.chat_view, name='chat'),
    path('discover/', views.discover_view, name='discover'),
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('orders/', views.orders_view, name='orders'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:profile_id>/', views.public_profile_view, name='public_profile'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]