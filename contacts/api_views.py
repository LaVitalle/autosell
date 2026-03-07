from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Contact
from .forms import ContactForm


@login_required
@require_http_methods(["GET"])
def api_list_contacts(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '').strip()

    contacts = Contact.objects.all().order_by('-created_at')

    if search:
        contacts = contacts.filter(name__icontains=search)

    total = contacts.count()
    start = (page - 1) * per_page
    end = start + per_page
    contacts_page = contacts[start:end]

    data = []
    for c in contacts_page:
        data.append({
            'id': c.id,
            'name': c.name,
            'phone': c.phone,
            'created_at': c.created_at.isoformat() if c.created_at else '',
        })

    return JsonResponse({
        'success': True,
        'contacts': data,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page,
    })


@login_required
@require_http_methods(["POST"])
def api_create_contact(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        contact = form.save()
        return JsonResponse({
            'success': True,
            'contact': {
                'id': contact.id,
                'name': contact.name,
                'phone': contact.phone,
            }
        }, status=201)
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_http_methods(["POST"])
def api_edit_contact(request, contact_id):
    try:
        contact = Contact.objects.get(id=contact_id)
    except Contact.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Contato não encontrado'}, status=404)

    form = ContactForm(request.POST, instance=contact)
    if form.is_valid():
        contact = form.save()
        return JsonResponse({
            'success': True,
            'contact': {
                'id': contact.id,
                'name': contact.name,
                'phone': contact.phone,
            }
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_http_methods(["POST"])
def api_delete_contact(request, contact_id):
    try:
        contact = Contact.objects.get(id=contact_id)
    except Contact.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Contato não encontrado'}, status=404)

    contact.delete()
    return JsonResponse({'success': True})
