from django.db import models


# Create your models here.
class Customer(models.Model):
    name = models.CharField(verbose_name='顧客姓名', max_length=10)
    phone = models.CharField(verbose_name='電話', max_length=15)
    passcode = models.CharField(verbose_name='暗號', max_length=10, null=True, blank=True)
    genderChoices = (('M', 'Female'), ('F', 'Female'), ('O', 'Other'),)
    gender = models.CharField(verbose_name='性別', max_length=1, choices=genderChoices)
    age = models.IntegerField(verbose_name='年齡')
