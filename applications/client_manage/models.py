from django.db import models


# Create your models here.
class ClientManage(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='snippets')

    class Meta:
        ordering = ('created',)
