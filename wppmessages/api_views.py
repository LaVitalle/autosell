from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from products.models import Product
from categories.models import Category
from .models import Message
from .forms import MessageForm
from utils.evoapi import send_media_message, send_text_message, build_product_text, send_product_message
from utils.api_response import api_success, api_error, api_form_error, api_exception


@login_required
@require_http_methods(["GET"])
def api_list_messages(request):
    try:
        page = max(1, int(request.GET.get('page', 1)))
    except (ValueError, TypeError):
        page = 1
    try:
        per_page = min(100, max(1, int(request.GET.get('per_page', 10))))
    except (ValueError, TypeError):
        per_page = 10
    search = request.GET.get('search', '').strip()

    messages = Message.objects.select_related('contact', 'product', 'category').order_by('-sent_at')

    if search:
        messages = messages.filter(
            Q(contact__name__icontains=search) |
            Q(product__name__icontains=search) |
            Q(category__name__icontains=search)
        )

    total = messages.count()
    start = (page - 1) * per_page
    end = start + per_page
    messages_page = messages[start:end]

    data = []
    for m in messages_page:
        content = ''
        if m.product:
            content = m.product.name
        elif m.category:
            content = m.category.name
        data.append({
            'id': m.id,
            'contact': m.contact.name,
            'type': m.type,
            'content': content,
            'status': m.status,
            'sent_at': m.sent_at.strftime('%d/%m %H:%M') if m.sent_at else '',
        })

    total_pages = (total + per_page - 1) // per_page

    total_messages = Message.objects.count()
    stats = {
        'total_messages': total_messages,
        'total_sent': Message.objects.filter(status='sent').count(),
        'total_failed': Message.objects.filter(status='failed').count(),
    }

    return api_success(
        data=data,
        message='Mensagens listadas com sucesso',
        page_info={
            'current': page,
            'per_page': per_page,
            'total_items': total,
            'total_pages': total_pages,
        },
        stats=stats,
    )


def _build_product_text(product):
    return build_product_text(product)


def _send_product_message(phone, product):
    return send_product_message(phone, product)


@login_required
@require_http_methods(["POST"])
def api_send_message(request):
    form = MessageForm(request.POST)
    if not form.is_valid():
        return api_form_error(form)

    try:
        message = form.save(commit=False)
        message.type = form.cleaned_data['send_type']
        message.status = 'pending'
        message.save()

        if message.type == 'product':
            product = message.product
            if not product:
                message.status = 'failed'
                message.save()
                return api_error(message='Produto nao encontrado', status_code=404)

            result = _send_product_message(message.contact.phone, product)
            if result:
                message.status = 'sent'
                message.save()
                return api_success(
                    data=[{
                        'id': message.id,
                        'contact': message.contact.name,
                        'type': message.type,
                        'content': product.name,
                        'status': 'sent',
                        'sent_at': message.sent_at.strftime('%d/%m %H:%M') if message.sent_at else '',
                    }],
                    message='Mensagem enviada com sucesso',
                )
            else:
                message.status = 'failed'
                message.save()
                return api_error(message='Falha ao enviar mensagem', status_code=500)

        elif message.type == 'category':
            category = message.category
            if not category:
                message.status = 'failed'
                message.save()
                return api_error(message='Categoria nao encontrada', status_code=404)

            products = category.products.exclude(stock_active=True, stock_quantity=0)
            total = products.count()
            if total == 0:
                message.status = 'failed'
                message.save()
                return api_error(message='Categoria sem produtos', status_code=400)
            failed_count = 0
            for product in products:
                try:
                    result = _send_product_message(message.contact.phone, product)
                    if not result:
                        failed_count += 1
                except Exception:
                    failed_count += 1

            if failed_count == 0:
                message.status = 'sent'
                status_msg = 'Todos os produtos enviados com sucesso'
                status_code = 200
            elif failed_count == total:
                message.status = 'failed'
                status_msg = 'Falha ao enviar todas as mensagens da categoria'
                status_code = 500
            else:
                message.status = 'sent'
                status_msg = f'{failed_count} de {total} produtos falharam ao enviar'
                status_code = 207

            message.save()
            return api_success(
                data=[{
                    'id': message.id,
                    'contact': message.contact.name,
                    'type': message.type,
                    'content': category.name,
                    'status': message.status,
                    'sent_at': message.sent_at.strftime('%d/%m %H:%M') if message.sent_at else '',
                    'failed_count': failed_count,
                    'total': total,
                }],
                message=status_msg,
                status_code=status_code,
            )

        message.status = 'failed'
        message.save()
        return api_error(message='Tipo de mensagem invalido', status_code=400)
    except Exception:
        return api_exception(request, 'wppmessages.api_views.api_send_message', 'Erro ao enviar mensagem')
