from django.urls import path
from . import views, api_views, webhook

urlpatterns = [
    path('', views.livechat, name='livechat'),
    path('hook/', webhook.webhook, name='livechat_hook'),

    # Conversations
    path('api/conversations/', api_views.api_conversations, name='livechat_conversations'),
    path('api/conversations/<int:conversation_id>/messages/', api_views.api_messages, name='livechat_messages'),
    path('api/conversations/<int:conversation_id>/send-text/', api_views.api_send_text, name='livechat_send_text'),
    path('api/conversations/<int:conversation_id>/send-product/', api_views.api_send_product, name='livechat_send_product'),
    path('api/conversations/<int:conversation_id>/send-category/', api_views.api_send_category, name='livechat_send_category'),
    path('api/conversations/<int:conversation_id>/mark-read/', api_views.api_mark_read, name='livechat_mark_read'),
    path('api/conversations/<int:conversation_id>/update-contact/', api_views.api_update_contact, name='livechat_update_contact'),
    path('api/conversations/start/', api_views.api_start_conversation, name='livechat_start_conversation'),
    path('api/conversations/<int:conversation_id>/delete/', api_views.api_delete_conversation, name='livechat_delete_conversation'),

    # Cart
    path('api/conversations/<int:conversation_id>/cart/', api_views.api_cart, name='livechat_cart'),
    path('api/conversations/<int:conversation_id>/cart/add/', api_views.api_cart_add, name='livechat_cart_add'),
    path('api/conversations/<int:conversation_id>/cart/update/', api_views.api_cart_update, name='livechat_cart_update'),
    path('api/conversations/<int:conversation_id>/cart/remove/<int:item_id>/', api_views.api_cart_remove, name='livechat_cart_remove'),
    path('api/conversations/<int:conversation_id>/cart/finalize/', api_views.api_cart_finalize, name='livechat_cart_finalize'),
    path('api/conversations/<int:conversation_id>/cart/clear/', api_views.api_cart_clear, name='livechat_cart_clear'),

    # Quick Sell
    path('api/conversations/<int:conversation_id>/quick-sell/', api_views.api_quick_sell, name='livechat_quick_sell'),

    # Global Poll
    path('api/poll/', api_views.api_poll, name='livechat_poll'),

    # Product/Category selectors
    path('api/products/', api_views.api_products_list, name='livechat_products'),
    path('api/categories/', api_views.api_categories_list, name='livechat_categories'),
]
