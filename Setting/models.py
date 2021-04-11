from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Setting(models.Model):
    key = models.CharField(verbose_name='key', max_length=20)
    value = models.JSONField(verbose_name='value')
    user = models.ForeignKey(User, verbose_name='使用者', on_delete=models.CASCADE)
