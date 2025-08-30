from django.contrib import admin
from .models import Product

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_active', 'stock_quantity', 'updated_at', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('stock_active', 'updated_at', 'created_at')
    ordering = ('-updated_at', '-created_at')
    list_per_page = 12
 
admin.site.register(Product, ProductAdmin)