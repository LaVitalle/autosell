import uuid
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Category
from .forms import CategoryForm
from products.models import Product
from utils.storage import upload_file, delete_file
from utils.api_response import api_success, api_error, api_form_error, api_exception


@login_required
@require_http_methods(["GET"])
def api_list_categories(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '').strip()

    categories = Category.objects.all().order_by('-id')

    if search:
        categories = categories.filter(name__icontains=search)

    total = categories.count()
    start = (page - 1) * per_page
    end = start + per_page
    categories_page = categories[start:end]

    data = []
    for c in categories_page:
        data.append({
            'id': c.id,
            'name': c.name,
            'description': c.description or '',
            'image_url': c.image_url or '',
            'products_count': c.products.count(),
        })

    total_pages = (total + per_page - 1) // per_page
    return api_success(
        data=data,
        message='Categorias listadas com sucesso',
        page_info={
            'current': page,
            'per_page': per_page,
            'total_items': total,
            'total_pages': total_pages,
        },
    )


@login_required
@require_http_methods(["POST"])
def api_create_category(request):
    try:
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            image = request.FILES.get("image_file")
            if image:
                file_name = f"categories/{uuid.uuid4()}{image.name}"
                img_url = upload_file(file_name, image)
                if img_url:
                    category.image_url = img_url
            category.save()

            selected_products = request.POST.getlist('products')
            if selected_products:
                product_ids = [int(pid) for pid in selected_products if pid.isdigit()]
                products = Product.objects.filter(id__in=product_ids)
                category.products.set(products)

            return api_success(
                data=[{
                    'id': category.id,
                    'name': category.name,
                    'image_url': category.image_url or '',
                    'products_count': category.products.count(),
                }],
                message='Categoria criada com sucesso',
                status_code=201,
            )
        return api_form_error(form)
    except Exception:
        return api_exception(request, 'categories.api_views.api_create_category', 'Erro ao criar categoria')


@login_required
@require_http_methods(["POST"])
def api_edit_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return api_error(message='Categoria nao encontrada', status_code=404)

    try:
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            image = request.FILES.get("image_file")
            if image:
                file_name = f"categories/{uuid.uuid4()}{image.name}"
                img_url = upload_file(file_name, image)
                if img_url:
                    delete_file(category.image_url)
                    category.image_url = img_url
            category.save()

            selected_products = request.POST.getlist('products')
            if selected_products:
                product_ids = [int(pid) for pid in selected_products if pid.isdigit()]
                products = Product.objects.filter(id__in=product_ids)
                category.products.set(products)
            else:
                category.products.clear()

            return api_success(
                data=[{
                    'id': category.id,
                    'name': category.name,
                    'image_url': category.image_url or '',
                    'products_count': category.products.count(),
                }],
                message='Categoria atualizada com sucesso',
            )
        return api_form_error(form)
    except Exception:
        return api_exception(request, 'categories.api_views.api_edit_category', 'Erro ao atualizar categoria')


@login_required
@require_http_methods(["POST"])
def api_delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return api_error(message='Categoria nao encontrada', status_code=404)

    if category.image_url:
        delete_file(category.image_url)
    category.delete()
    return api_success(message='Categoria excluida com sucesso')
