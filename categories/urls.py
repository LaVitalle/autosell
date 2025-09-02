from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_all_categories, name='get_all_categories'),
]

    # path('', views.get_all_products, name='get_all_products'),
    # path('/<int:product_id>', views.get_by_id, name='get_by_id'),
    # path('/create', views.create_product, name='create_product'),
    # path('/delete/<int:product_id>', views.delete_product, name='delete_by_id'),
    # path('/edit/<int:product_id>', views.edit_product, name='edit_product'),