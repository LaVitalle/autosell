from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from contacts.models import Contact
from products.models import Product
from categories.models import Category
from .models import Message
from .forms import MessageForm
from utils.evoapi import send_media_message, send_text_message
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

#message = TextMessage(
#    number="5511999999999",
#    text="Olá, como você está?",
#    delay=1000  # delay opcional em ms
#)

# Create your views here.
@login_required
def messages_manager(request):
    context = {
        'form': None,
        'contacts': Contact.objects.all(),
        'products': Product.objects.all(),
        'categories': Category.objects.all(),
        'messages_sent': Message.objects.all()[:10],
        'stats': get_stats()
    }
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.type = form.cleaned_data['send_type']
            message.status = 'pending'
            message.save()
            if message.type == 'product':
                product = Product.objects.get(id=message.product.id)
                if product:
                    if product.image_url:
                        result = send_media_message(
                            number=message.contact.phone,
                            mediatype='image', 
                            mimetype='image/png', 
                            caption=f'*{product.name}*\n{('_' + product.description + '_\n' if product.description else '')}\n\n{('*Restam:* ' + str(product.stock_quantity) + ' unidades\n' if product.stock_active else '')}*Preço:* R$ {product.price}',
                            media=product.image_url, 
                            fileName=f'{product.name}.png'
                        )
                        print(result)
                        if result:
                            message.status = 'sent'
                            message.save()
                            context['form'] = MessageForm()
                        else:
                            message.status = 'failed'
                            message.save()
                            context['form'] = MessageForm()
                    else:
                        result = send_text_message(message.contact.phone, f'*{product.name}*\n{('_' + product.description + '_\n' if product.description else '')}\n\n{('*Restam:* ' + str(product.stock_quantity) + ' unidades\n' if product.stock_active else '')}*Preço:* R$ {product.price}')
                        if result:
                            message.status = 'sent'
                            message.save()
                            context['form'] = MessageForm()
                        else:
                            message.status = 'failed'
                            message.save()
                            context['form'] = MessageForm()
                else:
                    message.status = 'failed'
                    message.save()
                    context['form'] = MessageForm()
                    context['request_status'] = 'failed'
                    context['request_message'] = 'Produto não encontrado'
            elif message.type == 'category':
                category = Category.objects.get(id=message.category.id)
                if category:
                    products = category.products.all()
                    if products.count() > 0:
                        total = products.count()
                        failed_count = 0
                        for product in products:
                            try:
                                if product.image_url:
                                    result = send_media_message(message.contact.phone, 'image', 'image/png', f'*{product.name}*\n{('_' + product.description + '_\n' if product.description else '')}\n\n{('*Restam:* ' + str(product.stock_quantity) + ' unidades\n' if product.stock_active else '')}*Preço:* R$ {product.price}', product.image_url, f'{product.name}.png')
                                else:
                                    result = send_text_message(message.contact.phone, f'*{product.name}*\n{('_' + product.description + '_\n' if product.description else '')}\n\n{('*Restam:* ' + str(product.stock_quantity) + ' unidades\n' if product.stock_active else '')}*Preço:* R$ {product.price}')
                                if not result:
                                    failed_count += 1
                            except Exception as e:
                                print(e)
                                failed_count += 1
                        if failed_count == 0:
                            message.status = 'sent'
                        elif failed_count == total:
                            message.status = 'failed'
                            context['request_status'] = 'failed'
                            context['request_message'] = 'Falha ao enviar todas as mensagens da categoria'
                        else:
                            message.status = 'sent'
                            context['request_status'] = 'warning'
                            context['request_message'] = f'{failed_count} de {total} produtos falharam ao enviar'
                        message.save()
                        context['form'] = MessageForm()
                    else:
                        message.status = 'failed'
                        message.save()
                        context['form'] = MessageForm()
                        context['request_status'] = 'failed'
                        context['request_message'] = 'Categoria sem produtos'
                else:
                    message.status = 'failed'
                    message.save()
                    context['form'] = MessageForm()
                    context['request_status'] = 'failed'
                    context['request_message'] = 'Categoria não encontrada'
            else:
                message.status = 'failed'
                message.save()
                context['form'] = MessageForm()
                context['request_status'] = 'failed'
                context['request_message'] = 'Tipo de mensagem não encontrado'
    else:
        context['form'] = MessageForm()
    return render(request, 'messages_manager.html', context)

### Auxiliar functions
def get_stats():
    """Get statistics for the dashboard cards"""
    return {
        'total_messages': Message.objects.count(),
        'total_contacts': Contact.objects.count(),
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count()
    }

@csrf_exempt
def hook(request):
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
    if client_ip != settings.EVOLUTION_SERVER_IP:
        return HttpResponseForbidden('Forbidden')
    body_string = request.body.decode('utf-8')
    send_text_message('5545998231771', str(body_string))
    return HttpResponse('OK')