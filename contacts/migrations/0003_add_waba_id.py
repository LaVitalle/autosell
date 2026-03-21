from django.db import migrations, models


def copy_phone_to_waba_id(apps, schema_editor):
    """Copia o valor atual de phone para waba_id nos contatos existentes."""
    Contact = apps.get_model('contacts', 'Contact')
    for contact in Contact.objects.all():
        contact.waba_id = contact.phone
        contact.phone = ''
        contact.save(update_fields=['waba_id', 'phone'])


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0002_alter_contact_phone'),
    ]

    operations = [
        # 1. Adiciona waba_id nullable temporariamente
        migrations.AddField(
            model_name='contact',
            name='waba_id',
            field=models.CharField(max_length=50, default='', help_text='WhatsApp ID extraido do remoteJid'),
            preserve_default=False,
        ),
        # 2. Copia phone -> waba_id e limpa phone
        migrations.RunPython(copy_phone_to_waba_id, migrations.RunPython.noop),
        # 3. Torna waba_id unique + indexed
        migrations.AlterField(
            model_name='contact',
            name='waba_id',
            field=models.CharField(max_length=50, unique=True, db_index=True, help_text='WhatsApp ID extraido do remoteJid'),
        ),
        # 4. Torna phone opcional
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.CharField(max_length=20, blank=True, default='', help_text='Numero de telefone real do contato'),
        ),
    ]
