from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(max_length=200)
    stock_active = models.BooleanField(default=False)
    stock_quantity = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        product = f'name: {self.name}, description: {self.description}, price: {self.price}, image_url: {self.image_url}, stock_active: {self.stock_active}, stock_quantity: {self.stock_quantity}, updated_at: {self.updated_at}, created_at: {self.created_at}'
        return product