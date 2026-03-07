from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from products.models import Product
from categories.models import Category
from .models import Message
from .forms import MessageForm
from utils.evoapi import send_media_message, send_text_message
from utils.api_response import api_success, api_error, api_form_error, api_exception


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
            media=f'{settings.SITE_URL}{product.image_url}',
            fileName=f'{product.name}.png'
        )
    return send_text_message(phone, text)


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
            try:
                product = Product.objects.get(id=message.product.id)
            except Product.DoesNotExist:
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
            try:
                category = Category.objects.get(id=message.category.id)
            except Category.DoesNotExist:
                message.status = 'failed'
                message.save()
                return api_error(message='Categoria nao encontrada', status_code=404)

            products = category.products.exclude(stock_active=True, stock_quantity=0)
            if products.count() == 0:
                message.status = 'failed'
                message.save()
                return api_error(message='Categoria sem produtos', status_code=400)

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
