from django.urls import path
from products import views

urlpatterns = [
    path('', views.get_all_products, name='get_all_products'),
    path('/<int:product_id>', views.get_by_id, name='get_by_id'),
    path('/create', views.create_product, name='create_product')
]