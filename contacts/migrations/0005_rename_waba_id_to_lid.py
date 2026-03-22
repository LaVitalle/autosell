from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0004_waba_id_nullable'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contact',
            old_name='waba_id',
            new_name='lid',
        ),
    ]
