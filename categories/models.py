from django.db import models
from products.models import Product

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=90)
    description = models.TextField(max_length=255, null=True, blank=False)
    image_url = models.URLField(max_length=500, null=True, blank=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(Product, related_name='categories')

    def __str__(self):
        return self.name