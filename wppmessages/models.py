from django.db import models
from contacts.models import Contact
from products.models import Product
from categories.models import Category

# Create your models here.
class Message(models.Model):
    TYPE_CHOICES = [
        ('product', 'Product'),
        ('category', 'Category'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='wppmessages', null=False, blank=False)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, null=False, blank=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wppmessages', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='wppmessages', null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=False, blank=False)

    def __str__(self):
        return f'{self.contact.name} - {self.product.name if self.product else self.category.name if self.category else ''} - {self.status} - {self.sent_at}'

    class Meta:
        ordering = ['-sent_at']