from django.db import models
from Stock.models import Material
from django.core.exceptions import ValidationError


# Create your models here.
class Menu(models.Model):
    name = models.CharField(verbose_name='分類名稱', max_length=10)
    customerAction = models.BooleanField(verbose_name='顧客操作', default=True)
    visible = models.BooleanField(verbose_name='顯示', default=True)


class Week(models.Model):
    name = models.CharField(verbose_name='星期名稱', max_length=10)


class Status(models.Model):
    name = models.CharField(verbose_name='狀態名稱', max_length=30)
    itemTypeChoices = (('N', 'Normal'), ('W', 'Special Week'), ('S', 'Special'), ('E', 'Weekend'), ('O', 'Off'),)
    itemType = models.CharField(verbose_name='狀態', max_length=2, choices=itemTypeChoices)
    startDate = models.DateField(verbose_name='開始日期', null=True, blank=True)
    endDate = models.DateField(verbose_name='結束日期', null=True, blank=True)
    week = models.ManyToManyField(Week, verbose_name='販售星期', blank=True)


def validate_file_size(value):
    filesize = value.size

    if filesize > 2097152:
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    else:
        return value


class MenuItem(models.Model):
    name = models.CharField(verbose_name='餐點名稱', max_length=30)
    menu = models.ForeignKey(Menu, verbose_name='目錄分類', default=1, on_delete=models.SET_DEFAULT, related_name='menuID')
    image = models.ImageField(upload_to='Menu/', null=True, blank=True, validators=[validate_file_size])
    price = models.DecimalField(decimal_places=2, max_digits=8, verbose_name='價格')
    menuSet = models.ManyToManyField("self", verbose_name='套餐內容', blank=True, symmetrical=False)
    description = models.CharField(verbose_name='描述', max_length=50)
    status = models.ForeignKey(Status, verbose_name='上架狀態', on_delete=models.SET_DEFAULT, default=1)


class Recipe(models.Model):
    menuItem = models.ForeignKey(MenuItem, verbose_name='餐點', on_delete=models.CASCADE, related_name='recipes')
    material = models.ForeignKey(Material, verbose_name='原料', on_delete=models.CASCADE)
    count = models.DecimalField(decimal_places=2, max_digits=8, verbose_name='數量')

    class Meta:
        unique_together = (('menuItem', 'material'))
