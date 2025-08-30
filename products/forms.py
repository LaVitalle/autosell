from django import forms
from .models import Product

#name = models.CharField(max_length=255)
#description = models.TextField()
#price = models.DecimalField(max_digits=10, decimal_places=2)
#image_url = models.URLField(max_length=200)
#stock_active = models.BooleanField(default=False)
#stock_quantity = models.IntegerField(default=0)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image_url', 'stock_active', 'stock_quantity']