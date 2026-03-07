from django.contrib import admin
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'updated_at', 'created_at')
    search_fields = ('name', 'phone')
    list_filter = ('updated_at', 'created_at')
    ordering = ('-updated_at', '-created_at')
    list_per_page = 12

admin.site.register(Contact, ContactAdmin)
