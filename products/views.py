from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm
from utils.storage import upload_file, delete_file
import uuid

# Create your views here.
@login_required
def get_all_products(request):
    return render(request, 'products.html')

@login_required
def stock_management(request):
    return render(request, 'stock.html')

@login_required
def get_by_id(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
    }
    return render(request, 'product.html', context)

@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            product = form.save(commit=False)
            image = request.FILES.get("image_file")
            if image:
                file_name = f"products/{str(uuid.uuid4()) + image.name}"
                img_url = upload_file(file_name, image)
                if img_url:
                    product.image_url = img_url
            product.save()
            return redirect('get_all_products')
        else:
            return render(request, 'product_form.html', {
                'form': form,
                'is_edit': False,
                'product': None,
                'page_title': 'Criar Produto',
                'page_subtitle': 'Adicione um novo produto ao seu catálogo',
                'submit_label': 'Criar Produto',
            })
    else:
        form = ProductForm()
        return render(request, 'product_form.html', {
            'form': form,
            'is_edit': False,
            'product': None,
            'page_title': 'Criar Produto',
            'page_subtitle': 'Adicione um novo produto ao seu catálogo',
            'submit_label': 'Criar Produto',
        })

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST' and request.POST['_method'] == 'DELETE':
        delete_file(product.image_url)
        product.delete()
        return redirect('get_all_products')
    else:
        return render(request, 'confirm_delete.html', {'product': product})
    
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
        'is_edit': True,
        'page_title': 'Editar Produto',
        'page_subtitle': 'Atualize as informações do produto',
        'submit_label': 'Salvar Alterações',
    }
    if request.method == 'POST':
        form = ProductForm(request.POST or None, request.FILES or None, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            image = request.FILES.get("image_file")
            if image:
                file_name = f"products/{str(uuid.uuid4()) + image.name}"
                img_url = upload_file(file_name, image)
                if img_url:
                    delete_file(product.image_url)
                    product.image_url = img_url
            product.save()
            return redirect('get_all_products')
    else:
        form = ProductForm(instance=product)
    context['form'] = form
    return render(request, 'product_form.html', context)