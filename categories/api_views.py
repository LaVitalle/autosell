import uuid
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Category
from .forms import CategoryForm
from products.models import Product
from utils.supabase_storage import upload_file_to_supabase, delete_file_from_supabase


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

    return JsonResponse({
        'success': True,
        'categories': data,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page,
    })


@login_required
@require_http_methods(["POST"])
def api_create_category(request):
    form = CategoryForm(request.POST, request.FILES)
    if form.is_valid():
        category = form.save(commit=False)
        image = request.FILES.get("image_file")
        if image:
            file_name = f"categories/{uuid.uuid4()}{image.name}"
            img_url = upload_file_to_supabase(file_name, image)
            if img_url:
                category.image_url = img_url
        category.save()

        selected_products = request.POST.getlist('products')
        if selected_products:
            product_ids = [int(pid) for pid in selected_products if pid.isdigit()]
            products = Product.objects.filter(id__in=product_ids)
            category.products.set(products)

        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'image_url': category.image_url or '',
                'products_count': category.products.count(),
            }
        }, status=201)
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_http_methods(["POST"])
def api_edit_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Categoria não encontrada'}, status=404)

    form = CategoryForm(request.POST, request.FILES, instance=category)
    if form.is_valid():
        category = form.save(commit=False)
        image = request.FILES.get("image_file")
        if image:
            file_name = f"categories/{uuid.uuid4()}{image.name}"
            img_url = upload_file_to_supabase(file_name, image)
            if img_url:
                delete_file_from_supabase(category.image_url)
                category.image_url = img_url
        category.save()

        selected_products = request.POST.getlist('products')
        if selected_products:
            product_ids = [int(pid) for pid in selected_products if pid.isdigit()]
            products = Product.objects.filter(id__in=product_ids)
            category.products.set(products)
        else:
            category.products.clear()

        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'image_url': category.image_url or '',
                'products_count': category.products.count(),
            }
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_http_methods(["POST"])
def api_delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Categoria não encontrada'}, status=404)

    if category.image_url:
        delete_file_from_supabase(category.image_url)
    category.delete()
    return JsonResponse({'success': True})
