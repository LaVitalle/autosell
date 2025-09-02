from django import forms
from .models import Product

#name = models.CharField(max_length=255)
#description = models.TextField()
#price = models.DecimalField(max_digits=10, decimal_places=2)
#image_url = models.URLField(max_length=200)
#stock_active = models.BooleanField(default=False)
#stock_quantity = models.IntegerField(default=0)

class ProductForm(forms.ModelForm):
    image_file = forms.FileField(required=False)

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock_active', 'stock_quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['stock_active'].required = False
        self.fields['stock_quantity'].required = False
        self.fields['image_file'].required = False
        self.fields['name'].required = True
        self.fields['price'].required = True
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("O nome do produto é obrigatório")
        if len(name) > 90:
            raise forms.ValidationError("O nome do produto deve ter menos de 90 caracteres")
        if len(name) <= 3:
            raise forms.ValidationError("O nome do produto deve ter mais de 3 caracteres")
        return name

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description:
            return None
        if len(description) > 255:
            raise forms.ValidationError("A descrição do produto deve ter menos de 255 caracteres")
        return description

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if not price:
            raise forms.ValidationError("O preço do produto é obrigatório")
        if price < 0:
            raise forms.ValidationError("O preço do produto não pode ser negativo")
        return price

    def clean_stock_active(self):
        stock_active = self.cleaned_data.get('stock_active')
        if stock_active is None:
            stock_active = False
        return stock_active

    def clean_stock_quantity(self):
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if not stock_quantity:
            stock_quantity = 0
        return stock_quantity

    def clean(self):
        stock_active = self.cleaned_data.get('stock_active')
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if not stock_active and stock_quantity > 0:
            self.cleaned_data['stock_quantity'] = 0
        return self.cleaned_data