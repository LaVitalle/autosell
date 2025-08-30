from django.shortcuts import render, redirect
from .models import Product
from .forms import ProductForm

# Create your views here.
def get_all_products(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'products.html', context)

def get_by_id(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {
        'product': product,
    }
    return render(request, 'product.html', context)

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('get_all_products')
    else:
        form = ProductForm()
    return render(request, 'create_product.html', {'form': form})