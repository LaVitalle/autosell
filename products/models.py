from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=90)
    description = models.TextField(max_length=255, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    image_url = models.URLField(max_length=500, null=True)
    stock_active = models.BooleanField(default=False, null=False, blank=False)
    stock_quantity = models.IntegerField(default=0, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        product = f'name: {self.name}, description: {self.description}, price: {self.price}, image_url: {self.image_url}, stock_active: {self.stock_active}, stock_quantity: {self.stock_quantity}, updated_at: {self.updated_at}, created_at: {self.created_at}'
        return product