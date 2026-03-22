import json
import uuid
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Sum, Count, F
from .models import Product
from .forms import ProductForm
from categories.models import Category
from utils.storage import upload_file, delete_file
from utils.api_response import api_success, api_error, api_form_error, api_exception


@login_required
@require_http_methods(["GET"])
def api_list_products(request):
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
    except (ValueError, TypeError):
        page, per_page = 1, 10
    per_page = min(per_page, 100)
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

    all_products = Product.objects.all()
    total_value = all_products.aggregate(total=Sum('price'))['total'] or 0
    stats = {
        'total_products': all_products.count(),
        'total_value': str(total_value),
        'with_stock_control': all_products.filter(stock_active=True).count(),
        'total_categories': Category.objects.count(),
    }

    return api_success(
        data=data,
        message='Produtos listados com sucesso',
        page_info={
            'current': page,
            'per_page': per_page,
            'total_items': total,
            'total_pages': total_pages,
        },
        stats=stats,
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


@login_required
@require_http_methods(["GET"])
def api_list_stock(request):
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
    except (ValueError, TypeError):
        page, per_page = 1, 10
    per_page = min(per_page, 100)
    search = request.GET.get('search', '').strip()
    stock_filter = request.GET.get('filter', 'all').strip()

    products = Product.objects.filter(stock_active=True).order_by('stock_quantity', 'name')

    if search:
        products = products.filter(name__icontains=search)

    if stock_filter == 'low':
        products = products.filter(stock_quantity__gt=0, stock_quantity__lte=F('stock_minimum'))
    elif stock_filter == 'out':
        products = products.filter(stock_quantity=0)

    total = products.count()
    start = (page - 1) * per_page
    end = start + per_page
    products_page = products[start:end]

    data = []
    for p in products_page:
        data.append({
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'image_url': p.image_url or '',
            'stock_quantity': p.stock_quantity,
            'stock_minimum': p.stock_minimum,
        })

    total_pages = (total + per_page - 1) // per_page

    all_stock = Product.objects.filter(stock_active=True)
    stats = {
        'total_limited': all_stock.count(),
        'low_stock': all_stock.filter(stock_quantity__gt=0, stock_quantity__lte=F('stock_minimum')).count(),
        'out_of_stock': all_stock.filter(stock_quantity=0).count(),
        'total_units': all_stock.aggregate(total=Sum('stock_quantity'))['total'] or 0,
    }

    return api_success(
        data=data,
        message='Estoque listado com sucesso',
        page_info={
            'current': page,
            'per_page': per_page,
            'total_items': total,
            'total_pages': total_pages,
        },
        stats=stats,
    )


@login_required
@require_http_methods(["POST"])
def api_bulk_update_stock(request):
    try:
        body = json.loads(request.body)
        updates = body.get('updates', [])

        if not updates or not isinstance(updates, list):
            return api_error(message='Lista de atualizacoes e obrigatoria', status_code=400)

        for item in updates:
            if not isinstance(item.get('id'), int):
                return api_error(message='ID do produto invalido', status_code=400)
            if item.get('mode') not in ('set', 'add'):
                return api_error(message='Modo deve ser "set" ou "add"', status_code=400)
            if not isinstance(item.get('value'), int) or item['value'] < 0:
                return api_error(message='Valor deve ser um inteiro >= 0', status_code=400)

        updated_count = 0
        errors = []

        with transaction.atomic():
            for item in updates:
                try:
                    product = Product.objects.select_for_update().get(
                        id=item['id'], stock_active=True
                    )
                    if item['mode'] == 'set':
                        product.stock_quantity = item['value']
                        product.save(update_fields=['stock_quantity', 'updated_at'])
                    else:
                        Product.objects.filter(id=item['id']).update(
                            stock_quantity=F('stock_quantity') + item['value']
                        )
                    updated_count += 1
                except Product.DoesNotExist:
                    errors.append(f'Produto {item["id"]} nao encontrado ou sem controle de estoque')

        message = f'{updated_count} produto(s) atualizado(s) com sucesso'
        if errors:
            message += f'. {len(errors)} erro(s): {"; ".join(errors)}'

        return api_success(
            data={'updated': updated_count, 'errors': errors},
            message=message,
            status_code=200 if not errors else 207,
        )
    except json.JSONDecodeError:
        return api_error(message='JSON invalido', status_code=400)
    except Exception:
        return api_exception(request, 'products.api_views.api_bulk_update_stock', 'Erro ao atualizar estoque')
