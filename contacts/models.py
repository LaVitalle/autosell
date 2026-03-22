from django.db import models

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=60, null=False, blank=False)
    lid = models.CharField(max_length=50, unique=True, null=True, blank=True, db_index=True, help_text='LID extraido do remoteJid')
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True, help_text='Numero de telefone real do contato (JID)')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name