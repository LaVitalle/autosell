from django.contrib import admin
from .models import Conversation, ChatMessage, Cart, CartItem, Sale, SaleItem


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('contact', 'remote_jid', 'last_message_text', 'last_message_at', 'unread_count')
    search_fields = ('contact__name', 'remote_jid')
    list_filter = ('last_message_direction',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('contact', 'direction', 'msg_type', 'content_preview', 'status', 'timestamp')
    list_filter = ('direction', 'msg_type', 'status')
    search_fields = ('content', 'contact__name')

    def content_preview(self, obj):
        return obj.content[:80] if obj.content else ''
    content_preview.short_description = 'Content'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact', 'status', 'created_at', 'finalized_at')
    list_filter = ('status',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'unit_price')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact', 'total', 'created_at')
    search_fields = ('contact__name',)


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product_name', 'quantity', 'unit_price')
