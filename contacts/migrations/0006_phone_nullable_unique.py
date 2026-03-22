from django.db import migrations, models


def convert_empty_phones_to_null(apps, schema_editor):
    """Converte phone='' para phone=None em todos os contatos."""
    Contact = apps.get_model('contacts', 'Contact')
    Contact.objects.filter(phone='').update(phone=None)


def convert_null_phones_to_empty(apps, schema_editor):
    """Reverso: converte phone=None para phone=''."""
    Contact = apps.get_model('contacts', 'Contact')
    Contact.objects.filter(phone__isnull=True).update(phone='')


def merge_duplicate_phones(apps, schema_editor):
    """Merge contatos que compartilham o mesmo phone (nao-nulo)."""
    Contact = apps.get_model('contacts', 'Contact')
    Conversation = apps.get_model('livechat', 'Conversation')
    ChatMessage = apps.get_model('livechat', 'ChatMessage')
    Cart = apps.get_model('livechat', 'Cart')
    Sale = apps.get_model('livechat', 'Sale')
    WppMessage = apps.get_model('wppmessages', 'Message')

    from django.db.models import Count

    dupes = (
        Contact.objects.filter(phone__isnull=False)
        .values('phone')
        .annotate(cnt=Count('id'))
        .filter(cnt__gt=1)
    )

    for dupe in dupes:
        phone_val = dupe['phone']
        contacts = list(Contact.objects.filter(phone=phone_val).order_by('id'))
        primary = contacts[0]

        for secondary in contacts[1:]:
            # Copiar lid do secondary para primary se primary nao tiver
            if not primary.lid and secondary.lid:
                primary.lid = secondary.lid
                primary.save(update_fields=['lid'])

            # Copiar nome se primary esta com nome generico
            if primary.name == (primary.lid or '') and secondary.name != (secondary.lid or ''):
                primary.name = secondary.name
                primary.save(update_fields=['name'])

            # Obter conversations
            primary_conv = None
            secondary_conv = None
            try:
                primary_conv = Conversation.objects.get(contact=primary)
            except Conversation.DoesNotExist:
                pass
            try:
                secondary_conv = Conversation.objects.get(contact=secondary)
            except Conversation.DoesNotExist:
                pass

            if secondary_conv:
                if primary_conv:
                    # Mover mensagens e carts do secondary conv para primary conv
                    ChatMessage.objects.filter(conversation=secondary_conv).update(
                        conversation=primary_conv, contact=primary)
                    Cart.objects.filter(conversation=secondary_conv).update(
                        conversation=primary_conv, contact=primary)

                    # Atualizar campos de resumo se secondary e mais recente
                    if (secondary_conv.last_message_at and
                        (not primary_conv.last_message_at or
                         secondary_conv.last_message_at > primary_conv.last_message_at)):
                        primary_conv.last_message_text = secondary_conv.last_message_text
                        primary_conv.last_message_at = secondary_conv.last_message_at
                        primary_conv.last_message_direction = secondary_conv.last_message_direction
                        primary_conv.save(update_fields=[
                            'last_message_text', 'last_message_at', 'last_message_direction'])

                    primary_conv.unread_count += secondary_conv.unread_count
                    primary_conv.save(update_fields=['unread_count'])

                    secondary_conv.delete()
                else:
                    # Reatribuir conversation do secondary para primary
                    secondary_conv.contact = primary
                    secondary_conv.save(update_fields=['contact'])

            # Reatribuir registros orfaos restantes
            ChatMessage.objects.filter(contact=secondary).update(contact=primary)
            Cart.objects.filter(contact=secondary).update(contact=primary)
            Sale.objects.filter(contact=secondary).update(contact=primary)
            WppMessage.objects.filter(contact=secondary).update(contact=primary)

            # Deletar contato duplicado
            secondary.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_rename_waba_id_to_lid'),
        ('livechat', '0001_initial'),
        ('wppmessages', '0003_initial'),
    ]

    operations = [
        # 1. Tornar phone nullable (remover default='')
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.CharField(
                max_length=20, null=True, blank=True,
                help_text='Numero de telefone real do contato (JID)'),
        ),
        # 2. Converter '' para None
        migrations.RunPython(convert_empty_phones_to_null, convert_null_phones_to_empty),
        # 3. Merge contatos duplicados
        migrations.RunPython(merge_duplicate_phones, migrations.RunPython.noop),
        # 4. Adicionar unique constraint
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.CharField(
                max_length=20, null=True, blank=True, unique=True, db_index=True,
                help_text='Numero de telefone real do contato (JID)'),
        ),
    ]
