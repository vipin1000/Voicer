from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('chat/<int:user_id>/', views.direct_chat_view, name='direct_chat'),
    path('discover/', views.discover_view, name='discover'),
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('orders/', views.orders_view, name='orders'),
    path('profile/<int:id>/', views.profile_view, name='profile'),
    path('profile_public/', views.public_profile_view, name='public_profile'),
    path('update_profile/', views.update_profile_view, name='update_profile'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email-step/', views.verify_email_step, name='verify_email_step'),
    path('place_order/', views.place_order_view, name='place_order'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
