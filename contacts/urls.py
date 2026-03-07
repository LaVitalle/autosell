from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.get_all_contacts, name='get_all_contacts'),
    path('create/', views.create_contact, name='create_contact'),
    path('edit/<int:contact_id>/', views.edit_contact, name='edit_contact'),
    path('delete/<int:contact_id>/', views.delete_contact, name='delete_contact'),
    # API endpoints
    path('api/', api_views.api_list_contacts, name='api_list_contacts'),
    path('api/create/', api_views.api_create_contact, name='api_create_contact'),
    path('api/<int:contact_id>/edit/', api_views.api_edit_contact, name='api_edit_contact'),
    path('api/<int:contact_id>/delete/', api_views.api_delete_contact, name='api_delete_contact'),
]
