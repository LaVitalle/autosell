from django.shortcuts import render, redirect
from contacts.models import Contact
from products.models import Product
from categories.models import Category
from .models import Message
from .forms import MessageForm
from utils.evoapi import send_media_message, send_text_message
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

#message = TextMessage(
#    number="5511999999999",
#    text="Olá, como você está?",
#    delay=1000  # delay opcional em ms
#)

# Create your views here.
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
                    if category.products.count() > 0:
                        try:
                            for product in category.products.all():
                                if product.image_url:
                                    try:
                                        result = send_media_message(message.contact.phone, 'image', 'image/png', f'*{product.name}*\n{('_' + product.description + '_\n' if product.description else '')}\n\n{('*Restam:* ' + str(product.stock_quantity) + ' unidades\n' if product.stock_active else '')}*Preço:* R$ {product.price}', product.image_url, f'{product.name}.png')
                                    except Exception as e:
                                        print(e)
                                        continue
                                else:
                                    try:
                                        result = send_text_message(message.contact.phone, f'*{product.name}*\n{('_' + product.description + '_\n' if product.description else '')}\n\n{('*Restam:* ' + str(product.stock_quantity) + ' unidades\n' if product.stock_active else '')}*Preço:* R$ {product.price}')
                                    except Exception as e:
                                        print(e)
                                        continue
                            message.status = 'sent'
                            message.save()
                            context['form'] = MessageForm()
                        except Exception as e:
                            message.status = 'failed'
                            message.save()
                            context['form'] = MessageForm()
                            context['request_status'] = 'failed'
                            context['request_message'] = 'Erro ao enviar mensagem de mídia ou texto'
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
    send_text_message('5545998231771', 'Fungou!')
    send_text_message('5545998231771', str(request.POST))
    return HttpResponse('OK')