from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.get_all_categories, name='get_all_categories'),
    path('<int:category_id>/', views.get_category_by_id, name='get_category_by_id'),
    path('create/', views.create_category, name='create_category'),
    path('edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete/<int:category_id>/', views.delete_category, name='delete_category'),
    # API endpoints
    path('api/', api_views.api_list_categories, name='api_list_categories'),
    path('api/create/', api_views.api_create_category, name='api_create_category'),
    path('api/<int:category_id>/edit/', api_views.api_edit_category, name='api_edit_category'),
    path('api/<int:category_id>/delete/', api_views.api_delete_category, name='api_delete_category'),
    path('api/<int:category_id>/remove-product/<int:product_id>/', api_views.api_remove_product, name='api_remove_product'),
]