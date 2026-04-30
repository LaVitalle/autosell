from django.urls import path
from products import views
from products import api_views

urlpatterns = [
    path('', views.get_all_products, name='get_all_products'),
    path('stock/', views.stock_management, name='stock_management'),
    path('<int:product_id>/', views.get_by_id, name='get_by_id'),
    path('create/', views.create_product, name='create_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_by_id'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    # API endpoints
    path('api/', api_views.api_list_products, name='api_list_products'),
    path('api/stock/', api_views.api_list_stock, name='api_list_stock'),
    path('api/stock/low/', api_views.api_list_low_stock, name='api_list_low_stock'),
    path('api/stock/bulk-update/', api_views.api_bulk_update_stock, name='api_bulk_update_stock'),
    path('api/create/', api_views.api_create_product, name='api_create_product'),
    path('api/<int:product_id>/edit/', api_views.api_edit_product, name='api_edit_product'),
    path('api/<int:product_id>/delete/', api_views.api_delete_product, name='api_delete_product'),
]