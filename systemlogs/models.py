from django.db import models
from django.contrib.auth.models import User


class SystemLog(models.Model):
    LEVEL_CHOICES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='ERROR')
    source = models.CharField(max_length=200)
    message = models.TextField()
    trace = models.TextField(blank=True, null=True)
    request_method = models.CharField(max_length=10, blank=True, null=True)
    request_path = models.CharField(max_length=500, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'System Log'
        verbose_name_plural = 'System Logs'

    def __str__(self):
        return f'[{self.level}] {self.source} - {self.message[:80]}'
