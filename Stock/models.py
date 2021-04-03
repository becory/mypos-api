from django.db import models


# Create your models here.
class Label(models.Model):
    name = models.CharField(verbose_name='分類名稱', max_length=10)


class Unit(models.Model):
    name = models.CharField(verbose_name='單位名稱', max_length=10)
    sign = models.CharField(verbose_name='單位符號', max_length=4)


class Material(models.Model):
    label = models.ForeignKey(Label, on_delete=models.SET_DEFAULT, verbose_name='分類', default=1,
                              related_name='materials')
    name = models.CharField(verbose_name='名稱', max_length=50)
    brand = models.CharField(verbose_name='品牌名稱', max_length=50)
    unit = models.ForeignKey(Unit, on_delete=models.SET_DEFAULT, verbose_name='單位', default=1)


class Stock(models.Model):
    stockDate = models.DateField(verbose_name="進貨時間", auto_now=True)
    expiryDate = models.DateField(verbose_name="有效期限")
    material = models.ForeignKey(Material, verbose_name='原料', on_delete=models.CASCADE)
    stock = models.DecimalField(decimal_places=2, max_digits=8, verbose_name='庫存')
