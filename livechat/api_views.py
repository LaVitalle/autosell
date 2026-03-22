import json
from decimal import Decimal
from datetime import datetime, timezone

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Q, F, Sum
from django.utils import timezone as dj_timezone

from contacts.models import Contact
from products.models import Product
from categories.models import Category
from .models import Conversation, ChatMessage, Cart, CartItem, Sale, SaleItem
from utils.api_response import api_success, api_error, api_exception, log_system_event
from utils.evoapi import send_text_message, send_product_message, build_product_text, build_catalog_text, mark_message_as_read, resolve_conversation_number


# ─── Conversations ───────────────────────────────────────────────────────────

@login_required
@require_http_methods(["GET"])
def api_conversations(request):
    try:
        search = request.GET.get('search', '').strip()
        page = max(1, int(request.GET.get('page', 1)))
        per_page = min(50, max(1, int(request.GET.get('per_page', 30))))

        qs = Conversation.objects.select_related('contact').filter(last_message_at__isnull=False)

        if search:
            qs = qs.filter(
                Q(contact__name__icontains=search) |
                Q(contact__phone__icontains=search)
            )

        total = qs.count()
        start = (page - 1) * per_page
        conversations = qs[start:start + per_page]

        data = []
        for c in conversations:
            data.append({
                'id': c.id,
                'contact_name': c.contact.name,
                'contact_phone': c.contact.phone or '',
                'remote_jid': c.remote_jid,
                'last_message_text': c.last_message_text,
                'last_message_at': c.last_message_at.isoformat() if c.last_message_at else None,
                'last_message_direction': c.last_message_direction,
                'unread_count': c.unread_count,
            })

        total_pages = (total + per_page - 1) // per_page

        return api_success(
            data=data,
            page_info={
                'current': page,
                'per_page': per_page,
                'total_items': total,
                'total_pages': total_pages,
            },
        )
    except Exception:
        return api_exception(request, 'livechat.api.conversations')


@login_required
@require_http_methods(["GET"])
def api_messages(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return api_error('Conversa nao encontrada', 404)

    try:
        after_id = request.GET.get('after_id')
        limit = min(100, max(1, int(request.GET.get('limit', 50))))
        status_since = request.GET.get('status_since')

        qs = ChatMessage.objects.filter(conversation=conversation).select_related('product', 'category')

        if after_id:
            qs = qs.filter(id__gt=int(after_id))

        messages = qs.order_by('timestamp')[:limit]

        data = []
        for m in messages:
            data.append({
                'id': m.id,
                'direction': m.direction,
                'msg_type': m.msg_type,
                'content': m.content,
                'product': _product_dict(m.product) if m.product else None,
                'category_name': m.category.name if m.category else None,
                'status': m.status,
                'timestamp': m.timestamp.isoformat(),
                'wpp_message_id': m.wpp_message_id,
            })

        status_updates = []
        if status_since:
            try:
                since_dt = datetime.fromisoformat(status_since)
                changed = ChatMessage.objects.filter(
                    conversation=conversation,
                    direction='out',
                    status_updated_at__gt=since_dt,
                ).values('id', 'status')[:100]
                status_updates = [{'id': c['id'], 'status': c['status']} for c in changed]
            except (ValueError, TypeError):
                pass

        return api_success(data=data, stats={'status_updates': status_updates} if status_updates else None)
    except Exception:
        return api_exception(request, 'livechat.api.messages')


@login_required
@require_http_methods(["POST"])
def api_send_text(request, conversation_id):
    try:
        conversation = Conversation.objects.select_related('contact').get(id=conversation_id)
    except Conversation.DoesNotExist:
        return api_error('Conversa nao encontrada', 404)

    try:
        body = json.loads(request.body)
        text = body.get('text', '').strip()
        if not text:
            return api_error('Texto vazio')

        # Prioriza phone (JID), fallback remote_jid (LID)
        number = resolve_conversation_number(conversation)
        result = send_text_message(number, text)
        if not result and number != conversation.remote_jid:
            result = send_text_message(conversation.remote_jid, text)

        log_system_event('INFO', 'livechat.api.send_text',
            f'Number: {number} | Result: {str(result)[:500]}')

        now = dj_timezone.now()
        wpp_id = None
        status = 'failed'
        if result:
            wpp_id = result.get('key', {}).get('id') if isinstance(result, dict) else None
            status = 'sent'

        msg = ChatMessage.objects.create(
            contact=conversation.contact,
            conversation=conversation,
            remote_jid=conversation.remote_jid,
            wpp_message_id=wpp_id,
            direction='out',
            msg_type='text',
            content=text,
            status=status,
            timestamp=now,
        )

        conversation.last_message_text = text[:200]
        conversation.last_message_at = now
        conversation.last_message_direction = 'out'
        conversation.save()

        if status == 'failed':
            return api_error('Falha ao enviar mensagem', 500)

        return api_success(data={
            'id': msg.id,
            'direction': 'out',
            'msg_type': 'text',
            'content': text,
            'status': status,
            'timestamp': now.isoformat(),
            'wpp_message_id': wpp_id,
        })
    except Exception:
        return api_exception(request, 'livechat.api.send_text')


@login_required
@require_http_methods(["POST"])
def api_send_product(request, conversation_id):
    try:
        conversation = Conversation.objects.select_related('contact').get(id=conversation_id)
    except Conversation.DoesNotExist:
        return api_error('Conversa nao encontrada', 404)

    try:
        body = json.loads(request.body)
        product_id = body.get('product_id')
        product = Product.objects.get(id=product_id)

        number = resolve_conversation_number(conversation)
        result = send_product_message(number, product)
        if not result and number != conversation.remote_jid:
            result = send_product_message(conversation.remote_jid, product)

        now = dj_timezone.now()
        wpp_id = None
        status = 'failed'
        if result:
            wpp_id = result.get('key', {}).get('id') if isinstance(result, dict) else None
            status = 'sent'

        content = build_product_text(product)
        msg = ChatMessage.objects.create(
            contact=conversation.contact,
            conversation=conversation,
            remote_jid=conversation.remote_jid,
            wpp_message_id=wpp_id,
            direction='out',
            msg_type='product',
            content=content,
            product=product,
            status=status,
            timestamp=now,
        )

        conversation.last_message_text = f'[Produto] {product.name}'[:200]
        conversation.last_message_at = now
        conversation.last_message_direction = 'out'
        conversation.save()

        if status == 'failed':
            return api_error('Falha ao enviar produto', 500)

        return api_success(data={
            'id': msg.id,
            'direction': 'out',
            'msg_type': 'product',
            'content': content,
            'product': _product_dict(product),
            'status': status,
            'timestamp': now.isoformat(),
        })
    except Product.DoesNotExist:
        return api_error('Produto nao encontrado', 404)
    except Exception:
        return api_exception(request, 'livechat.api.send_product')


@login_required
@require_http_methods(["POST"])
def api_send_category(request, conversation_id):
    try:
        conversation = Conversation.objects.select_related('contact').get(id=conversation_id)
    except Conversation.DoesNotExist:
        return api_error('Conversa nao encontrada', 404)

    try:
        body = json.loads(request.body)
        category_id = body.get('category_id')
        category = Category.objects.get(id=category_id)

        products = category.products.exclude(stock_active=True, stock_quantity=0)
        if not products.exists():
            return api_error('Categoria sem produtos disponiveis', 400)

        number = resolve_conversation_number(conversation)
        remote_jid = conversation.remote_jid
        sent_count = 0
        for product in products:
            result = send_product_message(number, product)
            if not result and number != remote_jid:
                result = send_product_message(remote_jid, product)
            if result:
                sent_count += 1

        now = dj_timezone.now()
        status = 'sent' if sent_count > 0 else 'failed'
        content = f'[Categoria] {category.name} ({sent_count}/{products.count()} enviados)'

        msg = ChatMessage.objects.create(
            contact=conversation.contact,
            conversation=conversation,
            remote_jid=conversation.remote_jid,
            direction='out',
            msg_type='category',
            content=content,
            category=category,
            status=status,
            timestamp=now,
        )

        conversation.last_message_text = content[:200]
        conversation.last_message_at = now
        conversation.last_message_direction = 'out'
        conversation.save()

        if status == 'failed':
            return api_error('Falha ao enviar categoria', 500)

        return api_success(data={
            'id': msg.id,
            'direction': 'out',
            'msg_type': 'category',
            'content': content,
            'category_name': category.name,
            'status': status,
            'timestamp': now.isoformat(),
        })
    except Category.DoesNotExist:
        return api_error('Categoria nao encontrada', 404)
    except Exception:
        return api_exception(request, 'livechat.api.send_category')


@login_required
@require_http_methods(["POST"])
def api_send_catalog(request, conversation_id):
    try:
        conversation = Conversation.objects.select_related('contact').get(id=conversation_id)
    except Conversation.DoesNotExist:
        return api_error('Conversa nao encontrada', 404)

    try:
        available = Product.objects.exclude(stock_active=True, stock_quantity=0)
        if not available.exists():
            return api_error('Nenhum produto disponivel', 400)

        # Agrupar por categoria
        categories = Category.objects.prefetch_related('products').all()
        categorized_ids = set()
        products_by_category = []

        for cat in categories:
            cat_products = [p for p in cat.products.all() if not (p.stock_active and p.stock_quantity == 0)]
            if cat_products:
                products_by_category.append((cat.name, cat_products))
                categorized_ids.update(p.id for p in cat_products)

        uncategorized = [p for p in available if p.id not in categorized_ids]

        text = build_catalog_text(products_by_category, uncategorized)

        number = resolve_conversation_number(conversation)
        result = send_text_message(number, text)
        if not result and number != conversation.remote_jid:
            result = send_text_message(conversation.remote_jid, text)

        now = dj_timezone.now()
        wpp_id = None
        status = 'failed'
        if result:
            wpp_id = result.get('key', {}).get('id') if isinstance(result, dict) else None
            status = 'sent'

        msg = ChatMessage.objects.create(
            contact=conversation.contact,
            conversation=conversation,
            remote_jid=conversation.remote_jid,
            wpp_message_id=wpp_id,
            direction='out',
            msg_type='catalog',
            content=text,
            status=status,
            timestamp=now,
        )

        conversation.last_message_text = '[Catalogo] Cardapio do Dia'[:200]
        conversation.last_message_at = now
        conversation.last_message_direction = 'out'
        conversation.save()

        if status == 'failed':
            return api_error('Falha ao enviar catalogo', 500)

        return api_success(data={
            'id': msg.id,
            'direction': 'out',
            'msg_type': 'catalog',
            'content': text,
            'status': status,
            'timestamp': now.isoformat(),
            'wpp_message_id': wpp_id,
        })
    except Exception:
        return api_exception(request, 'livechat.api.send_catalog')


@login_required
@require_http_methods(["POST"])
def api_mark_read(request, conversation_id):
    try:
        conversation = Conversation.objects.select_related('contact').get(id=conversation_id)
    except Conversation.DoesNotExist:
        return api_error('Conversa nao encontrada', 404)

    try:
        unread_qs = ChatMessage.objects.filter(
            conversation=conversation,
            direction='in',
        ).exclude(status='read')

        message_ids = list(
            unread_qs.exclude(wpp_message_id__isnull=True)
                     .exclude(wpp_message_id='')
                     .values_list('wpp_message_id', flat=True)
        )

        if message_ids:
            mark_message_as_read(conversation.remote_jid, message_ids)

        now = dj_timezone.now()
        unread_qs.update(status='read', status_updated_at=now)

        conversation.unread_count = 0
        conversation.save()

        return api_success(message='Mensagens marcadas como lidas')
    except Exception:
        return api_exception(request, 'livechat.api.mark_read')


# ─── Contact ─────────────────────────────────────────────────────────────────

@login_required
@require_http_methods(["POST"])
def api_update_contact(request, conversation_id):
    try:
        conversation = Conversation.objects.select_related('contact').get(id=conversation_id)
    except Conversation.DoesNotExist:
        return api_error('Conversa nao encontrada', 404)

    try:
        body = json.loads(request.body)
        name = body.get('name', '').strip()
        phone = body.get('phone')

        if not name and phone is None:
            return api_error('Nenhum dado para atualizar')

        contact = conversation.contact
        update_fields = []

        if name:
            contact.name = name
            update_fields.append('name')
        if phone is not None:
            contact.phone = phone.strip() or None
            update_fields.append('phone')

        contact.save(update_fields=update_fields)

        return api_success(data={'name': contact.name, 'phone': contact.phone or ''}, message='Contato atualizado')
    except Exception:
        return api_exception(request, 'livechat.api.update_contact')


# ─── Start / Delete Conversation ─────────────────────────────────────────────

@login_required
@require_http_methods(["POST"])
def api_start_conversation(request):
    try:
        body = json.loads(request.body)
        contact_id = body.get('contact_id')
        if not contact_id:
            return api_error('contact_id obrigatorio')

        try:
            contact = Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return api_error('Contato nao encontrado', 404)

        # Se ja existe conversa para esse contato, retornar ela
        try:
            conversation = Conversation.objects.get(contact=contact)
        except Conversation.DoesNotExist:
            # Criar nova conversa — usar phone ou lid como remote_jid
            remote_jid = contact.phone or contact.lid or str(contact.id)
            if '@' not in remote_jid:
                remote_jid = f'{remote_jid}@s.whatsapp.net'
            conversation = Conversation.objects.create(
                contact=contact,
                remote_jid=remote_jid,
            )

        return api_success(data={
            'id': conversation.id,
            'contact_name': contact.name,
            'contact_phone': contact.phone or '',
        }, message='Conversa iniciada')
    except Exception:
        return api_exception(request, 'livechat.api.start_conversation')


@login_required
@require_http_methods(["POST"])
def api_delete_conversation(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return api_error('Conversa nao encontrada', 404)

    try:
        conversation.delete()
        return api_success(message='Conversa excluida')
    except Exception:
        return api_exception(request, 'livechat.api.delete_conversation')


# ─── Cart ────────────────────────────────────────────────────────────────────

@login_required
@require_http_methods(["GET"])
def api_cart(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return api_error('Conversa nao encontrada', 404)

    try:
        cart = Cart.objects.filter(
            conversation=conversation, status='open'
        ).prefetch_related('items__product').first()

        if not cart:
            return api_success(data={'items': [], 'total': '0.00'})

        items = []
        total = Decimal('0.00')
        for item in cart.items.all():
            subtotal = item.unit_price * item.quantity
            total += subtotal
            items.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product.name,
                'product_image': item.product.image_url or '',
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'subtotal': str(subtotal),
            })

        return api_success(data={
            'cart_id': cart.id,
            'items': items,
            'total': str(total),
        })
    except Exception:
        return api_exception(request, 'livechat.api.cart')


@login_required
@require_http_methods(["POST"])
def api_cart_add(request, conversation_id):
    try:
        conversation = Conversation.objects.select_related('contact').get(id=conversation_id)
    except Conversation.DoesNotExist:
        return api_error('Conversa nao encontrada', 404)

    try:
        body = json.loads(request.body)
        product_id = body.get('product_id')
        quantity = max(1, int(body.get('quantity', 1)))

        product = Product.objects.get(id=product_id)

        cart, _ = Cart.objects.get_or_create(
            conversation=conversation,
            contact=conversation.contact,
            status='open',
        )

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'unit_price': product.price}
        )
        if not created:
            item.quantity += quantity
            item.unit_price = product.price
            item.save()

        return api_success(data={
            'item_id': item.id,
            'product_name': product.name,
            'quantity': item.quantity,
            'unit_price': str(item.unit_price),
        }, message='Produto adicionado ao carrinho')
    except Product.DoesNotExist:
        return api_error('Produto nao encontrado', 404)
    except Exception:
        return api_exception(request, 'livechat.api.cart_add')


@login_required
@require_http_methods(["POST"])
def api_cart_update(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return api_error('Conversa nao encontrada', 404)

    try:
        body = json.loads(request.body)
        item_id = body.get('item_id')
        quantity = int(body.get('quantity', 1))

        item = CartItem.objects.get(
            id=item_id,
            cart__conversation=conversation,
            cart__status='open'
        )

        if quantity <= 0:
            item.delete()
            return api_success(message='Item removido do carrinho')

        item.quantity = quantity
        item.save()

        return api_success(data={
            'item_id': item.id,
            'quantity': item.quantity,
        }, message='Quantidade atualizada')
    except CartItem.DoesNotExist:
        return api_error('Item nao encontrado', 404)
    except Exception:
        return api_exception(request, 'livechat.api.cart_update')


@login_required
@require_http_methods(["POST"])
def api_cart_remove(request, conversation_id, item_id):
    try:
        item = CartItem.objects.get(
            id=item_id,
            cart__conversation_id=conversation_id,
            cart__status='open'
        )
        item.delete()
        return api_success(message='Item removido do carrinho')
    except CartItem.DoesNotExist:
        return api_error('Item nao encontrado', 404)
    except Exception:
        return api_exception(request, 'livechat.api.cart_remove')


@login_required
@require_http_methods(["POST"])
def api_cart_finalize(request, conversation_id):
    try:
        conversation = Conversation.objects.select_related('contact').get(id=conversation_id)
    except Conversation.DoesNotExist:
        return api_error('Conversa nao encontrada', 404)

    try:
        cart = Cart.objects.filter(
            conversation=conversation, status='open'
        ).prefetch_related('items__product').first()

        if not cart:
            return api_error('Nenhum carrinho aberto')

        cart_items = list(cart.items.all())
        if not cart_items:
            return api_error('Carrinho vazio')

        with transaction.atomic():
            total = Decimal('0.00')
            for item in cart_items:
                if item.product.stock_active:
                    updated = Product.objects.filter(
                        id=item.product_id,
                        stock_active=True,
                        stock_quantity__gte=item.quantity
                    ).update(stock_quantity=F('stock_quantity') - item.quantity)
                    if updated == 0:
                        raise ValueError(f'Estoque insuficiente: {item.product.name}')
                total += item.unit_price * item.quantity

            sale = Sale.objects.create(
                contact=conversation.contact,
                cart=cart,
                total=total,
            )
            for item in cart_items:
                SaleItem.objects.create(
                    sale=sale,
                    product=item.product,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )

            cart.status = 'finalized'
            cart.finalized_at = dj_timezone.now()
            cart.save()

        return api_success(data={
            'sale_id': sale.id,
            'total': str(total),
        }, message='Venda finalizada com sucesso')
    except ValueError as e:
        return api_error(str(e), 400)
    except Exception:
        return api_exception(request, 'livechat.api.cart_finalize')


@login_required
@require_http_methods(["POST"])
def api_cart_clear(request, conversation_id):
    try:
        cart = Cart.objects.filter(
            conversation_id=conversation_id, status='open'
        ).first()

        if cart:
            cart.status = 'cancelled'
            cart.save()

        return api_success(message='Carrinho limpo')
    except Exception:
        return api_exception(request, 'livechat.api.cart_clear')


# ─── Quick Sell ──────────────────────────────────────────────────────────────

@login_required
@require_http_methods(["POST"])
def api_quick_sell(request, conversation_id):
    try:
        conversation = Conversation.objects.select_related('contact').get(id=conversation_id)
    except Conversation.DoesNotExist:
        return api_error('Conversa nao encontrada', 404)

    try:
        body = json.loads(request.body)
        product_id = body.get('product_id')
        quantity = max(1, int(body.get('quantity', 1)))

        product = Product.objects.get(id=product_id)

        with transaction.atomic():
            if product.stock_active:
                updated = Product.objects.filter(
                    id=product.id,
                    stock_active=True,
                    stock_quantity__gte=quantity
                ).update(stock_quantity=F('stock_quantity') - quantity)
                if updated == 0:
                    return api_error(f'Estoque insuficiente: {product.name}', 400)

            total = product.price * quantity
            sale = Sale.objects.create(
                contact=conversation.contact,
                total=total,
            )
            SaleItem.objects.create(
                sale=sale,
                product=product,
                product_name=product.name,
                quantity=quantity,
                unit_price=product.price,
            )

        return api_success(data={
            'sale_id': sale.id,
            'total': str(total),
        }, message='Venda realizada com sucesso')
    except Product.DoesNotExist:
        return api_error('Produto nao encontrado', 404)
    except Exception:
        return api_exception(request, 'livechat.api.quick_sell')


# ─── Global Poll ─────────────────────────────────────────────────────────────

@login_required
@require_http_methods(["GET"])
def api_poll(request):
    try:
        since = request.GET.get('since')
        qs = Conversation.objects.filter(last_message_at__isnull=False)

        if since:
            try:
                since_dt = datetime.fromisoformat(since)
                qs = qs.filter(last_message_at__gt=since_dt)
            except (ValueError, TypeError):
                pass

        conversations = qs.values(
            'id', 'last_message_text', 'last_message_at',
            'last_message_direction', 'unread_count', 'contact__name'
        )[:50]

        total_unread = Conversation.objects.filter(
            unread_count__gt=0
        ).aggregate(total=Sum('unread_count'))['total'] or 0

        data = []
        for c in conversations:
            data.append({
                'id': c['id'],
                'contact_name': c['contact__name'],
                'last_message_text': c['last_message_text'],
                'last_message_at': c['last_message_at'].isoformat() if c['last_message_at'] else None,
                'last_message_direction': c['last_message_direction'],
                'unread_count': c['unread_count'],
            })

        return api_success(data=data, stats={'total_unread': total_unread})
    except Exception:
        return api_exception(request, 'livechat.api.poll')


# ─── Products/Categories List for Selectors ──────────────────────────────────

@login_required
@require_http_methods(["GET"])
def api_products_list(request):
    try:
        search = request.GET.get('search', '').strip()
        category_id = request.GET.get('category_id')

        qs = Product.objects.all()
        if search:
            qs = qs.filter(name__icontains=search)
        if category_id:
            qs = qs.filter(categories__id=category_id)

        qs = qs.exclude(stock_active=True, stock_quantity=0)

        products = qs[:50]
        data = [_product_dict(p) for p in products]
        return api_success(data=data)
    except Exception:
        return api_exception(request, 'livechat.api.products_list')


@login_required
@require_http_methods(["GET"])
def api_categories_list(request):
    try:
        categories = Category.objects.all()[:50]
        data = [{
            'id': c.id,
            'name': c.name,
            'description': c.description or '',
            'image_url': c.image_url or '',
        } for c in categories]
        return api_success(data=data)
    except Exception:
        return api_exception(request, 'livechat.api.categories_list')


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _product_dict(product):
    return {
        'id': product.id,
        'name': product.name,
        'description': product.description or '',
        'price': str(product.price),
        'image_url': product.image_url or '',
        'stock_active': product.stock_active,
        'stock_quantity': product.stock_quantity,
    }
