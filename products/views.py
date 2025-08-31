from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm
from utils.supabase_storage import upload_file_to_supabase, delete_file_from_supabase
import uuid

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
        form = ProductForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            product = form.save(commit=False)
            image = request.FILES.get("image_file")
            if image:
                file_name = f"products/{str(uuid.uuid4()) + image.name}"
                img_url = upload_file_to_supabase(file_name, image)
                if img_url:
                    product.image_url = img_url
            product.save()
            return redirect('get_all_products')
    else:
        form = ProductForm()
        return render(request, 'create_product.html', {'form': form})

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST' and request.POST['_method'] == 'DELETE':
        delete_file_from_supabase(product.image_url)
        product.delete()
        return redirect('get_all_products')
    else:
        return render(request, 'confirm_delete.html', {'product': product})
    
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST or None, request.FILES or None, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            image = request.FILES.get("image_file")
            if image:
                file_name = f"products/{str(uuid.uuid4()) + image.name}"
                img_url = upload_file_to_supabase(file_name, image)
                if img_url:
                    delete_file_from_supabase(product.image_url)
                    product.image_url = img_url
            product.save()
            return redirect('get_all_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form, 'product': product})