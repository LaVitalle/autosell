from django.contrib import admin
from .models import SystemLog


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'source', 'message_short', 'request_method', 'request_path', 'user', 'created_at']
    list_filter = ['level', 'created_at', 'request_method']
    search_fields = ['source', 'message', 'request_path']
    readonly_fields = ['level', 'source', 'message', 'trace', 'request_method', 'request_path', 'user', 'created_at']
    list_per_page = 50

    def message_short(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_short.short_description = 'Mensagem'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
