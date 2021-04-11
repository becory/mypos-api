# Generated by Django 3.1.7 on 2021-04-12 00:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Menu', '0001_initial'),
        ('Customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=10, verbose_name='方式')),
                ('className', models.CharField(blank=True, max_length=10, null=True, verbose_name='狀態英文名稱')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checkOut', models.BooleanField(default=False, verbose_name='結帳')),
                ('orderID', models.IntegerField(null=True, verbose_name='序號')),
                ('desk', models.IntegerField(default=0, null=True, verbose_name='桌號')),
                ('createDateTime', models.DateTimeField(auto_now_add=True, null=True, verbose_name='產生時間')),
                ('confirmDateTime', models.DateTimeField(blank=True, null=True, verbose_name='訂單確認時間')),
                ('checkoutDateTime', models.DateTimeField(blank=True, null=True, verbose_name='訂單結帳時間')),
                ('finishDateTime', models.DateTimeField(blank=True, null=True, verbose_name='訂單完成時間')),
                ('pickupDateTime', models.DateTimeField(blank=True, null=True, verbose_name='訂單完成時間')),
                ('orderFrom', models.CharField(choices=[('C', 'Customer'), ('S', 'Store'), ('F', 'FoodPanda'), ('U', 'UberEats')], max_length=2, verbose_name='訂單來源')),
                ('checkOutTotal', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='已收金額')),
                ('customer', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='Customer.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='狀態名稱')),
                ('className', models.CharField(max_length=10, verbose_name='狀態英文名稱')),
                ('icon', models.CharField(max_length=50, verbose_name='狀態圖示')),
                ('orderNo', models.IntegerField(verbose_name='順序')),
                ('visible', models.BooleanField(verbose_name='顯示')),
            ],
        ),
        migrations.CreateModel(
            name='OrderDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transactionItem', models.CharField(max_length=30, verbose_name='實際交易儲存餐點名稱')),
                ('transactionCost', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='實際交易金額')),
                ('count', models.IntegerField(verbose_name='數量')),
                ('remark', models.CharField(blank=True, max_length=100, null=True, verbose_name='備註')),
                ('cook', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Order.cook')),
                ('menuItem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menuItems', to='Menu.menuitem')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderDetails', to='Order.order')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='Order.status'),
        ),
    ]
