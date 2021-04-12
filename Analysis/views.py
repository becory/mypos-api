from django.db import models
from django.db.models import F, ExpressionWrapper
from django.db.models.functions import Cast
from django.db.models.fields import DateField
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import FieldDoesNotExist
# Create your views here.
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from Analysis.serializers import AnalysisSerializer
from Auth.views import IsAdminSuperUser
from Order.models import *
from Stock.models import *
from Customer.models import *
from Menu.models import *

from rest_framework.decorators import authentication_classes, permission_classes, action

from Setting.models import Setting
from Setting.serializers import SettingUpdateSerializers


class AnalysisViewSet(viewsets.ViewSet):
    serializer_class = AnalysisSerializer
    model = OrderDetail
    queryset = OrderDetail.objects.all()
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [permissions.IsAuthenticated]

    # list_filter_parameter = []
    # filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    # ordering_fields = []
    # filterset_fields = []
    # search_fields = []
    # modelName = None
    # pagination_class = StandardPagination()

    def get_serializer_class(self):
        if self.action == 'list':
            if hasattr(self, 'list_serializer_class'):
                return self.list_serializer_class
        elif self.action == 'retrieve':
            if hasattr(self, 'retrieve_serializer_class'):
                return self.retrieve_serializer_class
        return self.serializer_class

    def get_queryset(self):
        return self.model.objects.all().order_by('pk')

    # def filter_queryset(self, queryset):
    #     for backend in list(self.filter_backends):
    #         queryset = backend().filter_queryset(self.request, queryset, view=self)
    #     return queryset

    @method_decorator(name='list', decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='app',
                in_=openapi.IN_QUERY,
                description='aggregation',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='aggregation',
                in_=openapi.IN_QUERY,
                description='aggregation',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='name',
                in_=openapi.IN_QUERY,
                description='name',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='value',
                in_=openapi.IN_QUERY,
                description='value',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='start_date',
                in_=openapi.IN_QUERY,
                description='start_date',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                name='end_date',
                in_=openapi.IN_QUERY,
                description='end_date',
                type=openapi.TYPE_STRING
            )
        ],
        # filter_inspectors=[DjangoFilterDescriptionInspector]
    ))
    def list(self, request):
        app = self.request.query_params.get('app', False)
        aggregation = self.request.query_params.get('aggregation', False)
        name = self.request.query_params.get('name', False)
        value = self.request.query_params.get('value', False)
        queryFilter = dict(self.request.query_params)
        already_use = ['app', 'aggregation', 'name', 'value']
        for item in already_use:
            queryFilter.pop(item, None)
        print(queryFilter)
        if aggregation:
            if globals()[app]._meta.get_field(name).get_internal_type() == 'DateTimeField':
                name = Cast(F(name), output_field=DateField())
            elif globals()[app]._meta.get_field(name).get_internal_type() == 'ForeignKey':
                try:
                    globals()[app]._meta.get_field(name).related_model._meta.get_field('name')
                    name = F(name + "__name")
                except FieldDoesNotExist:
                    name = F(name + "__label")
            else:
                name = F(name)

            if 'start_date' in queryFilter and 'end_date' in queryFilter:
                if app == 'Order':
                    filterQuery = {"createDateTime__range": [queryFilter['start_date'][0], queryFilter['end_date'][0]]}
                elif app == 'OrderDetail':
                    filterQuery = {"order__createDateTime__range": [queryFilter['start_date'][0], queryFilter['end_date'][0]]}
                elif app == 'Stock':
                    filterQuery = {"stockDate__range": [queryFilter['start_date'][0], queryFilter['end_date'][0]]}
                result = globals()[app].objects.filter(**filterQuery)
            else:
                result = globals()[app].objects
            result = result.values(**{'name': name}).order_by('name').annotate(
                **{'value': getattr(models, aggregation)(value)})
            totalcount = result.count()
            # result = self.pagination_class.paginate_queryset(queryset=result, request=request, view=self)
            serializer = self.get_serializer_class()(result, many=True)
            data = serializer.data
        return Response({"totalCount": totalcount, "aggregation": aggregation, "result": data})

    @action(detail=False, methods=['get'])
    @method_decorator(name='list', decorator=swagger_auto_schema())
    def App(self, request):
        total = [
            {'label': '銷售分析', 'value': 'Order'},
            {'label': '銷售品項分析', 'value': 'OrderDetail'},
            {'label': '庫存分析', 'value': 'Stock'}
        ]
        return Response({"result": total})

    @action(detail=False, methods=['get'])
    @method_decorator(name='list', decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='app',
                in_=openapi.IN_QUERY,
                description='aggregation',
                type=openapi.TYPE_STRING
            ),
        ]))
    def Columns(self, request):
        app = self.request.query_params.get('app', False)
        total = {
            'Order': [
                {'label': '顧客', 'value': 'customer'},
                {'label': '訂單來源', 'value': 'orderFrom'},
                {'label': '產生訂單時間', 'value': 'createDateTime'},
                {'label': '桌號', 'value': 'desk'},
                {'label': '訂單狀態', 'value': 'status'},
                {'label': '結帳', 'value': 'checkOut'}
            ],
            'OrderDetail': [
                {'label': '品項', 'value': 'menuItem'},
                {'label': '烹調方式', 'value': 'cook'}
            ],
            'Stock': [
                {'label': '原料', 'value': 'material'}
            ]
        }
        if app:
            return Response({"result": total[app]})

    @action(detail=False, methods=['get'])
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='app',
                in_=openapi.IN_QUERY,
                description='aggregation',
                type=openapi.TYPE_STRING
            ),
        ])
    def Value(self, request):
        app = self.request.query_params.get('app', False)
        total = {
            'Order': [
                {'label': '結帳金額', 'value': 'checkOutTotal'}
            ],
            'OrderDetail': [
                {'label': '數量', 'value': 'count'}
            ],
            'Stock': [
                {'label': '庫存', 'value': 'stock'}
            ]
        }
        if app:
            return Response({"result": total[app]})

    @action(detail=False, methods=['put', 'get'])
    @swagger_auto_schema(
        manual_parameters=[])
    def Setting(self, request):
        if self.request.method == 'GET':
            try:
                instance = Setting.objects.get(key='Analysis', user=self.request.user)
                data = getattr(instance, 'value')
                print('data', data)
            except Setting.DoesNotExist:
                data = [{"width": 8, "app": "Order", "name": "createDateTime", "value": "checkOutTotal",
                         "aggregation": "Sum", "chart": "line"},
                        {"width": 8, "app": "OrderDetail", "name": "menuItem", "value": "count", "aggregation": "Sum",
                         "chart": "pie"},
                        {"width": 8, "app": "Stock", "name": "material", "value": "stock", "aggregation": "Sum",
                         "chart": "bar"}]
            return Response(data)
        elif self.request.method == 'PUT':
            data = {"key": "Analysis", "value": request.data, "user": request.user}
            try:
                instance = Setting.objects.get(key='Analysis', user=self.request.user)
                serializer = SettingUpdateSerializers(instance, data=data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
            except Setting.DoesNotExist:
                serializer = SettingUpdateSerializers(data=data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
            data = serializer.data
            return Response(data)
