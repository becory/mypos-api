from django.db import models
from Customer.models import Customer
from Menu.models import MenuItem


# Create your models here.
class Status(models.Model):
    name = models.CharField(verbose_name='狀態名稱', max_length=10)
    className = models.CharField(verbose_name='狀態英文名稱', max_length=10)
    icon = models.CharField(verbose_name='狀態圖示', max_length=50)
    orderNo = models.IntegerField(verbose_name='順序')
    visible = models.BooleanField(verbose_name='顯示')


class Order(models.Model):
    status = models.ForeignKey(Status, on_delete=models.SET_DEFAULT, default=1)
    customer = models.ForeignKey(Customer, on_delete=models.SET_DEFAULT, default=1)
    checkOut = models.BooleanField(verbose_name='結帳', default=False)
    orderID = models.IntegerField(verbose_name='序號', null=True)
    desk = models.IntegerField(verbose_name='桌號', null=True, default=0)
    createDateTime = models.DateTimeField(verbose_name='產生時間', auto_now_add=True, null=True, blank=True)
    confirmDateTime = models.DateTimeField(verbose_name='訂單確認時間', null=True, blank=True)
    checkoutDateTime = models.DateTimeField(verbose_name='訂單結帳時間', null=True, blank=True)
    finishDateTime = models.DateTimeField(verbose_name='訂單完成時間', null=True, blank=True)
    pickupDateTime = models.DateTimeField(verbose_name='訂單完成時間', null=True, blank=True)
    orderFromChoices = (('C', 'Customer'), ('S', 'Store'), ('F', 'FoodPanda'), ('U', 'UberEats'),)
    orderFrom = models.CharField(verbose_name='訂單來源', choices=orderFromChoices, max_length=2)
    checkOutTotal = models.DecimalField(decimal_places=2, max_digits=8, verbose_name='已收金額', null=True, blank=True)


class Cook(models.Model):
    label = models.CharField(verbose_name='方式', max_length=10)
    className = models.CharField(verbose_name='狀態英文名稱', max_length=10, null=True, blank=True)


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderDetails')
    menuItem = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='menuItems')
    transactionItem = models.CharField(verbose_name='實際交易儲存餐點名稱', max_length=30)
    transactionCost = models.DecimalField(decimal_places=2, max_digits=8, verbose_name='實際交易金額')
    count = models.IntegerField(verbose_name='數量')
    cook = models.ForeignKey(Cook, on_delete=models.CASCADE, null=True, blank=True)
    remark = models.CharField(verbose_name='備註', max_length=100, null=True, blank=True)
