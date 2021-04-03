from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser, MultiPartParser
from .models import Menu, Week, Status, MenuItem
from .serializers import MenuSerializer, WeekSerializer, StatusSerializer, StatusCreateSerializer, MenuItemSerializer, \
    MenuItemCreateSerializer, MenuCreateSerializer, MenuItemImageSerializer
from patches.viewset import BasicViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.
dateFormatList = ['year', 'month', 'day']
timeFormatList = ['hour', 'minute', 'second']


class MenuViewSet(BasicViewSet):
    model = Menu
    queryset = model.objects.all()
    serializer_class = MenuSerializer
    create_serializer_class = MenuCreateSerializer
    update_serializer_class = MenuCreateSerializer
    partial_update_serializer_class = MenuCreateSerializer
    filterset_fields = []
    for item in serializer_class.get_fields(serializer_class):
        if item != 'passcode':
            filterset_fields.append(item)
    ordering_fields = ['name', 'customerAction', 'visible']
    search_fields = ['name', 'customerAction', 'visible']
    modelName = Menu.__name__

    @swagger_auto_schema(operation_summary='Get Menu List',
                         operation_description='Get Menu List',
                         manual_parameters=[
                             openapi.Parameter(
                                 name='columns',
                                 in_=openapi.IN_QUERY,
                                 description='columns',
                                 type=openapi.TYPE_BOOLEAN
                             )
                         ],
                         )
    def list(self, request):
        return super().list(request)

    @swagger_auto_schema(
        request_body=serializer_class,
        responses={404: 'not found'}
    )
    def create(self, request):
        return super().create(request)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def retrieve(self, request, pk):
        return super().retrieve(request, pk)

    @swagger_auto_schema(
        request_body=serializer_class
    )
    def update(self, request, pk=None):
        return super().update(request, pk)

    @swagger_auto_schema(
        request_body=serializer_class
    )
    def partial_update(self, request, pk=None):
        return super().partial_update(request, pk)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def destroy(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), RS_ID=pk)
        serializer = self.serializer_class(instance)
        data = serializer.data
        self.get_queryset()
        return Response(data)


class WeekViewSet(BasicViewSet):
    model = Week
    queryset = model.objects.all()
    serializer_class = WeekSerializer
    filterset_fields = []
    for item in serializer_class.get_fields(serializer_class):
        if item != 'passcode':
            filterset_fields.append(item)
    ordering_fields = ['name']
    search_fields = ['name']
    modelName = Week.__name__

    @swagger_auto_schema(operation_summary='Get Week List',
                         operation_description='Get Week List',
                         manual_parameters=[
                             openapi.Parameter(
                                 name='columns',
                                 in_=openapi.IN_QUERY,
                                 description='columns',
                                 type=openapi.TYPE_BOOLEAN
                             )
                         ],
                         )
    def list(self, request):
        return super().list(request)

    @swagger_auto_schema(
        request_body=serializer_class,
        responses={404: 'not found'}
    )
    def create(self, request):
        return super().create(request)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def retrieve(self, request, pk):
        return super().retrieve(request, pk)

    @swagger_auto_schema(
        request_body=serializer_class
    )
    def update(self, request, pk=None):
        return super().update(request, pk)

    @swagger_auto_schema(
        request_body=serializer_class
    )
    def partial_update(self, request, pk=None):
        return super().partial_update(request, pk)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def destroy(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), RS_ID=pk)
        serializer = self.serializer_class(instance)
        data = serializer.data
        self.get_queryset()
        return Response(data)


class StatusViewSet(BasicViewSet):
    model = Status
    queryset = model.objects.all()
    serializer_class = StatusSerializer
    create_serializer_class = StatusCreateSerializer
    update_serializer_class = StatusCreateSerializer
    partial_update_serializer_class = StatusCreateSerializer
    filterset_fields = []
    for item in serializer_class.get_fields(serializer_class):
        if item != 'passcode':
            filterset_fields.append(item)
    ordering_fields = ['name', 'itemType', 'startDate', 'endDate', 'week']
    search_fields = ['name', 'itemType', 'startDate', 'endDate', 'week']
    modelName = Status.__name__

    @swagger_auto_schema(operation_summary='Get Status List',
                         operation_description='Get Status List',
                         manual_parameters=[
                             openapi.Parameter(
                                 name='columns',
                                 in_=openapi.IN_QUERY,
                                 description='columns',
                                 type=openapi.TYPE_BOOLEAN
                             )
                         ],
                         )
    def list(self, request):
        return super().list(request)

    @swagger_auto_schema(
        request_body=create_serializer_class,
        responses={404: 'not found'}
    )
    def create(self, request):
        return super().create(request)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def retrieve(self, request, pk):
        return super().retrieve(request, pk)

    @swagger_auto_schema(
        request_body=create_serializer_class
    )
    def update(self, request, pk=None):
        return super().update(request, pk)

    @swagger_auto_schema(
        request_body=create_serializer_class
    )
    def partial_update(self, request, pk=None):
        return super().partial_update(request, pk)


class MenuItemViewSet(BasicViewSet):
    model = MenuItem
    queryset = model.objects.all()
    serializer_class = MenuItemSerializer
    create_serializer_class = MenuItemCreateSerializer
    update_serializer_class = MenuItemCreateSerializer
    partial_update_serializer_class = MenuItemCreateSerializer
    filterset_fields = []
    for item in serializer_class.get_fields(serializer_class):
        if item != 'image':
            filterset_fields.append(item)
    ordering_fields = ['name', 'menu', 'price', 'material', 'menuSet', 'description', 'status']
    search_fields = ['name', 'menu', 'price', 'material', 'menuSet', 'description', 'status']
    modelName = MenuItem.__name__

    @swagger_auto_schema(operation_summary='Get MenuItem List',
                         operation_description='Get MenuItem List',
                         manual_parameters=[
                             openapi.Parameter(
                                 name='columns',
                                 in_=openapi.IN_QUERY,
                                 description='columns',
                                 type=openapi.TYPE_BOOLEAN
                             )
                         ],
                         )
    def list(self, request):
        return super().list(request)

    @swagger_auto_schema(
        request_body=create_serializer_class,
        responses={404: 'not found'}
    )
    def create(self, request):
        return super().create(request)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def retrieve(self, request, pk):
        return super().retrieve(request, pk)

    @swagger_auto_schema(
        request_body=create_serializer_class
    )
    def update(self, request, pk=None):
        return super().update(request, pk)

    @swagger_auto_schema(
        request_body=create_serializer_class
    )
    def partial_update(self, request, pk=None):
        return super().partial_update(request, pk)

    @swagger_auto_schema(
        responses={404: 'not found'}
    )
    def destroy(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.serializer_class(instance)
        data = serializer.data
        self.get_queryset()
        instance.delete()
        return Response(data)

    @swagger_auto_schema(
        request_body=MenuItemImageSerializer
    )
    @action(detail=True, methods=['put'], parser_classes=(MultiPartParser, FileUploadParser))
    def Upload(self, request, pk=None):
        serializer = MenuItemImageSerializer(data=request.data)  # <------ note the request.FILES
        serializer.is_valid(raise_exception=True)
        instance = self.model.objects.get(pk=pk)
        serializer.update(instance, validated_data=request.data)
        return Response(status=204)

    @action(detail=True, methods=['get'])
    def File(self, request, pk=None):
        instance = self.model.objects.get(pk=pk)
        serializer = MenuItemImageSerializer(instance)
        return Response(serializer.data)
