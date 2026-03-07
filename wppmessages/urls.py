from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.messages_manager, name='messages_manager'),
    path('hook/', views.hook, name='hook'),
    # API endpoints
    path('api/', api_views.api_list_messages, name='api_list_messages'),
    path('api/send/', api_views.api_send_message, name='api_send_message'),
]