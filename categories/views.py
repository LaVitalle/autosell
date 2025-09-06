from django.shortcuts import render, get_object_or_404, redirect
import uuid
from utils.supabase_storage import upload_file_to_supabase, delete_file_from_supabase
from .models import Category
from .forms import CategoryForm
from products.models import Product

# Create your views here.
def get_all_categories(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})

def get_category_by_id(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = category.products.all()
    
    context = {
        'category': category,
        'products': products,
        'total_products': products.count(),
    }
    
    return render(request, 'category.html', context)

def create_category(request):
    # Importar Product model
    from products.models import Product
    
    if request.method == 'POST':
        form = CategoryForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            category = form.save(commit=False)
            image = request.FILES.get("image_file")
            if image:
                file_name = f"categories/{str(uuid.uuid4()) + image.name}"
                img_url = upload_file_to_supabase(file_name, image)
                if img_url:
                    category.image_url = img_url
            category.save()
            
            # Processar produtos selecionados
            selected_products = request.POST.getlist('products')
            if selected_products:
                # Converter IDs para inteiros e filtrar produtos existentes
                product_ids = [int(pid) for pid in selected_products if pid.isdigit()]
                products = Product.objects.filter(id__in=product_ids)
                category.products.set(products)
            
            return redirect('get_all_categories')
    else:
        form = CategoryForm()
    
    # Buscar todos os produtos para o JavaScript
    all_products = Product.objects.all().order_by('name')
    
    context = {
        'form': form,
        'all_products': all_products
    }
    
    return render(request, 'create_category.html', context)

def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST or None, request.FILES or None, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            image = request.FILES.get("image_file")
            if image:
                file_name = f"categories/{str(uuid.uuid4()) + image.name}"
                img_url = upload_file_to_supabase(file_name, image)
                if img_url:
                    delete_file_from_supabase(category.image_url)
                    category.image_url = img_url
            category.save()
            
            # Processar produtos selecionados
            selected_products = request.POST.getlist('products')
            if selected_products:
                # Converter IDs para inteiros e filtrar produtos existentes
                product_ids = [int(pid) for pid in selected_products if pid.isdigit()]
                products = Product.objects.filter(id__in=product_ids)
                category.products.set(products)
            else:
                # Se nenhum produto foi selecionado, limpar a associação
                category.products.clear()
            
            return redirect('get_all_categories')
    else:
        form = CategoryForm(instance=category)
    
    # Buscar todos os produtos para o JavaScript
    all_products = Product.objects.all().order_by('name')
    
    context = {
        'form': form,
        'category': category,
        'all_products': all_products
    }
    return render(request, 'edit_category.html', context)

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST' and request.POST['_method'] == 'DELETE':
        # Deletar imagem do Supabase se existir
        if category.image_url:
            delete_file_from_supabase(category.image_url)
        category.delete()
        return redirect('get_all_categories')
    else:
        return render(request, 'confirm_delete_category.html', {'category': category})