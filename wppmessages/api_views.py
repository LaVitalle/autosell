from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from contacts.models import Contact
from products.models import Product
from categories.models import Category
from .models import Message
from .forms import MessageForm
from utils.evoapi import send_media_message, send_text_message


def _build_product_text(product):
    parts = [f'*{product.name}*']
    if product.description:
        parts.append(f'_{product.description}_')
    parts.append('')
    if product.stock_active:
        parts.append(f'*Restam:* {product.stock_quantity} unidades')
    parts.append(f'*Preco:* R$ {product.price}')
    return '\n'.join(parts)


def _send_product_message(phone, product):
    text = _build_product_text(product)
    if product.image_url:
        return send_media_message(
            number=phone,
            mediatype='image',
            mimetype='image/png',
            caption=text,
            media=product.image_url,
            fileName=f'{product.name}.png'
        )
    return send_text_message(phone, text)


@login_required
@require_http_methods(["POST"])
def api_send_message(request):
    form = MessageForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    message = form.save(commit=False)
    message.type = form.cleaned_data['send_type']
    message.status = 'pending'
    message.save()

    if message.type == 'product':
        try:
            product = Product.objects.get(id=message.product.id)
        except Product.DoesNotExist:
            message.status = 'failed'
            message.save()
            return JsonResponse({'success': False, 'error': 'Produto não encontrado'}, status=404)

        result = _send_product_message(message.contact.phone, product)
        if result:
            message.status = 'sent'
            message.save()
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'contact': message.contact.name,
                    'type': message.type,
                    'content': product.name,
                    'status': 'sent',
                    'sent_at': message.sent_at.strftime('%d/%m %H:%M') if message.sent_at else '',
                }
            })
        else:
            message.status = 'failed'
            message.save()
            return JsonResponse({'success': False, 'error': 'Falha ao enviar mensagem'}, status=500)

    elif message.type == 'category':
        try:
            category = Category.objects.get(id=message.category.id)
        except Category.DoesNotExist:
            message.status = 'failed'
            message.save()
            return JsonResponse({'success': False, 'error': 'Categoria não encontrada'}, status=404)

        products = category.products.all()
        if products.count() == 0:
            message.status = 'failed'
            message.save()
            return JsonResponse({'success': False, 'error': 'Categoria sem produtos'}, status=400)

        total = products.count()
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
        elif failed_count == total:
            message.status = 'failed'
            status_msg = 'Falha ao enviar todas as mensagens da categoria'
        else:
            message.status = 'sent'
            status_msg = f'{failed_count} de {total} produtos falharam ao enviar'

        message.save()
        return JsonResponse({
            'success': failed_count < total,
            'message': {
                'id': message.id,
                'contact': message.contact.name,
                'type': message.type,
                'content': category.name,
                'status': message.status,
                'sent_at': message.sent_at.strftime('%d/%m %H:%M') if message.sent_at else '',
            },
            'detail': status_msg,
            'failed_count': failed_count,
            'total': total,
        })

    message.status = 'failed'
    message.save()
    return JsonResponse({'success': False, 'error': 'Tipo de mensagem inválido'}, status=400)
