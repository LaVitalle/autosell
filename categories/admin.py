from django.contrib import admin
from .models import Category
# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image_url', 'updated_at', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('updated_at', 'created_at')
    ordering = ('-updated_at', '-created_at')
    list_per_page = 12

admin.site.register(Category, CategoryAdmin)