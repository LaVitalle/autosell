from django.db import models

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=60, null=False, blank=False)
    phone = models.CharField(max_length=20, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name