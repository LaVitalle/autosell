from django.urls import path
from . import views

urlpatterns = [
    path('', views.messages_manager, name='messages_manager'),
    path('hook', views.hook, name='hook'),
]