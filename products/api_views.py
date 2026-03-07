import uuid
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Product
from .forms import ProductForm
from utils.storage import upload_file, delete_file
from utils.api_response import api_success, api_error, api_form_error, api_exception


@login_required
@require_http_methods(["GET"])
def api_list_products(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '').strip()

    products = Product.objects.all().order_by('-created_at')

    if search:
        products = products.filter(name__icontains=search)

    total = products.count()
    start = (page - 1) * per_page
    end = start + per_page
    products_page = products[start:end]

    data = []
    for p in products_page:
        data.append({
            'id': p.id,
            'name': p.name,
            'description': p.description or '',
            'price': str(p.price),
            'image_url': p.image_url or '',
            'stock_active': p.stock_active,
            'stock_quantity': p.stock_quantity,
            'created_at': p.created_at.isoformat() if p.created_at else '',
        })

    total_pages = (total + per_page - 1) // per_page
    return api_success(
        data=data,
        message='Produtos listados com sucesso',
        page_info={
            'current': page,
            'per_page': per_page,
            'total_items': total,
            'total_pages': total_pages,
        },
    )


@login_required
@require_http_methods(["POST"])
def api_create_product(request):
    try:
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            image = request.FILES.get("image_file")
            if image:
                file_name = f"products/{uuid.uuid4()}{image.name}"
                img_url = upload_file(file_name, image)
                if img_url:
                    product.image_url = img_url
            product.save()
            return api_success(
                data=[{
                    'id': product.id,
                    'name': product.name,
                    'price': str(product.price),
                    'image_url': product.image_url or '',
                }],
                message='Produto criado com sucesso',
                status_code=201,
            )
        return api_form_error(form)
    except Exception:
        return api_exception(request, 'products.api_views.api_create_product', 'Erro ao criar produto')


@login_required
@require_http_methods(["POST"])
def api_edit_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return api_error(message='Produto nao encontrado', status_code=404)

    try:
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            image = request.FILES.get("image_file")
            if image:
                file_name = f"products/{uuid.uuid4()}{image.name}"
                img_url = upload_file(file_name, image)
                if img_url:
                    delete_file(product.image_url)
                    product.image_url = img_url
            product.save()
            return api_success(
                data=[{
                    'id': product.id,
                    'name': product.name,
                    'price': str(product.price),
                    'image_url': product.image_url or '',
                }],
                message='Produto atualizado com sucesso',
            )
        return api_form_error(form)
    except Exception:
        return api_exception(request, 'products.api_views.api_edit_product', 'Erro ao atualizar produto')


@login_required
@require_http_methods(["POST"])
def api_delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return api_error(message='Produto nao encontrado', status_code=404)

    if product.image_url:
        delete_file(product.image_url)
    product.delete()
    return api_success(message='Produto excluido com sucesso')
