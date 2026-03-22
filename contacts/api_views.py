from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from .models import Contact
from .forms import ContactForm
from utils.api_response import api_success, api_error, api_form_error, api_exception


@login_required
@require_http_methods(["GET"])
def api_list_contacts(request):
    try:
        page = max(1, int(request.GET.get('page', 1)))
    except (ValueError, TypeError):
        page = 1
    try:
        per_page = min(100, max(1, int(request.GET.get('per_page', 10))))
    except (ValueError, TypeError):
        per_page = 10
    search = request.GET.get('search', '').strip()

    contacts = Contact.objects.all().order_by('-created_at')

    if search:
        contacts = contacts.filter(Q(name__icontains=search) | Q(phone__icontains=search))

    contacts = contacts.annotate(message_count=Count('wppmessages'))

    total = contacts.count()
    start = (page - 1) * per_page
    end = start + per_page
    contacts_page = contacts[start:end]

    data = []
    for c in contacts_page:
        data.append({
            'id': c.id,
            'name': c.name,
            'phone': c.phone or '',
            'created_at': c.created_at.isoformat() if c.created_at else '',
            'message_count': c.message_count,
        })

    total_pages = (total + per_page - 1) // per_page

    stats = {
        'total_contacts': Contact.objects.count(),
    }

    return api_success(
        data=data,
        message='Contatos listados com sucesso',
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
def api_create_contact(request):
    try:
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            return api_success(
                data=[{
                    'id': contact.id,
                    'name': contact.name,
                    'phone': contact.phone or '',
                }],
                message='Contato criado com sucesso',
                status_code=201,
            )
        return api_form_error(form)
    except Exception:
        return api_exception(request, 'contacts.api_views.api_create_contact', 'Erro ao criar contato')


@login_required
@require_http_methods(["POST"])
def api_edit_contact(request, contact_id):
    try:
        contact = Contact.objects.get(id=contact_id)
    except Contact.DoesNotExist:
        return api_error(message='Contato nao encontrado', status_code=404)

    try:
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            return api_success(
                data=[{
                    'id': contact.id,
                    'name': contact.name,
                    'phone': contact.phone or '',
                }],
                message='Contato atualizado com sucesso',
            )
        return api_form_error(form)
    except Exception:
        return api_exception(request, 'contacts.api_views.api_edit_contact', 'Erro ao atualizar contato')


@login_required
@require_http_methods(["POST"])
def api_delete_contact(request, contact_id):
    try:
        contact = Contact.objects.get(id=contact_id)
    except Contact.DoesNotExist:
        return api_error(message='Contato nao encontrado', status_code=404)

    contact.delete()
    return api_success(message='Contato excluido com sucesso')
