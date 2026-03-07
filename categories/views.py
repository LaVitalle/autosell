from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from utils.storage import delete_file
from .models import Category
from .forms import CategoryForm
from products.models import Product

# Create your views here.
@login_required
def get_all_categories(request):
    return render(request, 'categories.html')

@login_required
def get_category_by_id(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = category.products.all()
    
    context = {
        'category': category,
        'products': products,
        'total_products': products.count(),
    }
    
    return render(request, 'category.html', context)

@login_required
def create_category(request):
    form = CategoryForm(request.POST or None, request.FILES or None) if request.method == 'POST' else CategoryForm()

    all_products = Product.objects.all().order_by('name')

    context = {
        'form': form,
        'all_products': all_products,
        'is_edit': False,
        'page_title': 'Nova Categoria',
        'page_subtitle': 'Crie uma nova categoria e adicione produtos',
        'submit_label': 'Criar Categoria',
    }

    return render(request, 'category_form.html', context)

@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    form = CategoryForm(request.POST or None, request.FILES or None, instance=category) if request.method == 'POST' else CategoryForm(instance=category)

    all_products = Product.objects.all().order_by('name')

    context = {
        'form': form,
        'category': category,
        'all_products': all_products,
        'is_edit': True,
        'page_title': 'Editar Categoria',
        'page_subtitle': 'Modifique os dados da categoria e seus produtos',
        'submit_label': 'Salvar Alterações',
    }

    return render(request, 'category_form.html', context)

@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST' and request.POST['_method'] == 'DELETE':
        # Deletar imagem do disco se existir
        if category.image_url:
            delete_file(category.image_url)
        category.delete()
        return redirect('get_all_categories')
    else:
        return render(request, 'confirm_delete_category.html', {'category': category})