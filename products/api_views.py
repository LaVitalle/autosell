import uuid
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Product
from .forms import ProductForm
from utils.supabase_storage import upload_file_to_supabase, delete_file_from_supabase


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

    return JsonResponse({
        'success': True,
        'products': data,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page,
    })


@login_required
@require_http_methods(["POST"])
def api_create_product(request):
    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
        product = form.save(commit=False)
        image = request.FILES.get("image_file")
        if image:
            file_name = f"products/{uuid.uuid4()}{image.name}"
            img_url = upload_file_to_supabase(file_name, image)
            if img_url:
                product.image_url = img_url
        product.save()
        return JsonResponse({
            'success': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'image_url': product.image_url or '',
            }
        }, status=201)
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_http_methods(["POST"])
def api_edit_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produto não encontrado'}, status=404)

    form = ProductForm(request.POST, request.FILES, instance=product)
    if form.is_valid():
        product = form.save(commit=False)
        image = request.FILES.get("image_file")
        if image:
            file_name = f"products/{uuid.uuid4()}{image.name}"
            img_url = upload_file_to_supabase(file_name, image)
            if img_url:
                delete_file_from_supabase(product.image_url)
                product.image_url = img_url
        product.save()
        return JsonResponse({
            'success': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'image_url': product.image_url or '',
            }
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_http_methods(["POST"])
def api_delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produto não encontrado'}, status=404)

    if product.image_url:
        delete_file_from_supabase(product.image_url)
    product.delete()
    return JsonResponse({'success': True})
