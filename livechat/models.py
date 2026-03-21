from django.db import models
from contacts.models import Contact
from products.models import Product
from categories.models import Category


class Conversation(models.Model):
    contact = models.OneToOneField(Contact, on_delete=models.CASCADE, related_name='conversation')
    remote_jid = models.CharField(max_length=50, unique=True, db_index=True)
    last_message_text = models.CharField(max_length=200, blank=True, default='')
    last_message_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_message_direction = models.CharField(max_length=3, blank=True, default='')
    unread_count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_message_at']

    def __str__(self):
        return f'{self.contact.name} ({self.remote_jid})'


class ChatMessage(models.Model):
    DIRECTION_CHOICES = [('in', 'Incoming'), ('out', 'Outgoing')]
    TYPE_CHOICES = [
        ('text', 'Text'),
        ('product', 'Product'),
        ('category', 'Category'),
        ('image', 'Image'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='chat_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    remote_jid = models.CharField(max_length=50, db_index=True)
    wpp_message_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    direction = models.CharField(max_length=3, choices=DIRECTION_CHOICES)
    msg_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='text')
    content = models.TextField(blank=True, default='')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    status_updated_at = models.DateTimeField(null=True, blank=True, db_index=True)
    timestamp = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['remote_jid', 'timestamp']),
            models.Index(fields=['contact', '-timestamp']),
        ]

    def __str__(self):
        return f'{self.direction}: {self.content[:50]}'


class Cart(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('finalized', 'Finalized'),
        ('cancelled', 'Cancelled'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='carts')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='carts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    finalized_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Cart #{self.id} - {self.contact.name} ({self.status})'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'


class Sale(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='sales')
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Sale #{self.id} - R${self.total}'


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=90)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product_name} x{self.quantity}'
