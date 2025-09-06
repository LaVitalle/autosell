from django.db import models

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=60, null=False, blank=False)
    phone = models.CharField(max_length=20, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'name: {self.name}, phone: {self.phone}, updated_at: {self.updated_at}, created_at: {self.created_at}'