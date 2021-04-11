from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication

from pos.const import fieldDict, inputFieldDict, dateFormat
from django.shortcuts import get_object_or_404
from rest_framework import status, authentication, permissions
from rest_framework import viewsets
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_yasg.inspectors.query import CoreAPICompatInspector
from drf_yasg.inspectors import NotHandled
from .serializers import ColumnsSerializer, SelectionSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from patches.api import StandardPagination
from rest_framework.decorators import action

# Create your views here.
dateFormatList = ['year', 'month', 'day']
timeFormatList = ['hour', 'minute', 'second']


class IsAdminSuperUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff and request.user.is_superuser)


class DjangoFilterDescriptionInspector(CoreAPICompatInspector):

    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            result = super(DjangoFilterDescriptionInspector, self).get_filter_parameters(filter_backend)
            for param in result:
                if not param.get('description', ''):
                    param.description = "Filter the returned list by {field_name}".format(field_name=param.name)

            return result

        return NotHandled


class BasicViewSet(viewsets.ViewSet):
    serializer_class = None
    model = None
    queryset = None
    list_filter_parameter = []
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = []
    filterset_fields = []
    search_fields = []
    modelName = None
    pagination_class = StandardPagination()
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            if hasattr(self, 'list_serializer_class'):
                return self.list_serializer_class
        elif self.action == 'create':
            if hasattr(self, 'create_serializer_class'):
                return self.create_serializer_class
        elif self.action == 'retrieve':
            if hasattr(self, 'retrieve_serializer_class'):
                return self.retrieve_serializer_class
        elif self.action == 'update':
            if hasattr(self, 'update_serializer_class'):
                return self.update_serializer_class
        elif self.action == 'partial_update':
            if hasattr(self, 'partial_update_serializer_class'):
                return self.partial_update_serializer_class
        elif self.action == 'Form':
            if hasattr(self, 'create_serializer_class'):
                return self.create_serializer_class
        return self.serializer_class

    def get_queryset(self):
        return self.model.objects.all().order_by('pk')

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        return queryset

    @method_decorator(name='list', decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='columns',
                in_=openapi.IN_QUERY,
                description='columns',
                type=openapi.TYPE_BOOLEAN
            )
        ],
        filter_inspectors=[DjangoFilterDescriptionInspector]
    ))
    def list(self, request):
        columns = self.request.query_params.get('columns', False)
        selection = self.request.query_params.get('selection', False)
        if selection:
            children = self.request.query_params.get('children', False)
            if children:
                children = {"source": children, "selection": selection}
            else:
                children = {"selection": selection}
                # try:
            result = self.filter_queryset(self.get_queryset())
            return Response(SelectionSerializer(result, many=True, context=children).data)
            # except:
            #     return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if columns == 'true':
            fields = self.model._meta.fields
            fields = list(filter(lambda item: item.name in [item for item in
                                                            self.get_serializer_class().get_fields(
                                                                self.get_serializer_class())],
                                 fields))
            fields = [{"label": item.verbose_name, "field": item.name, "type": fieldDict()[item.get_internal_type()],
                       "inputType": inputFieldDict()[item.get_internal_type()], **dateFormat(item.get_internal_type()),
                       "sortable": True} for item in fields]
            return Response(ColumnsSerializer(fields, many=True).data)
        result = self.filter_queryset(self.get_queryset())
        totalcount = result.count()
        result = self.pagination_class.paginate_queryset(queryset=result, request=request, view=self)
        serializer = self.get_serializer_class()(result, many=True)
        data = serializer.data
        return Response({"totalCount": totalcount, "result": data})

    # @swagger_auto_schema(
    #     request_body=serializer_class
    # )
    def create(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        return Response(data)

    @action(detail=False, methods=['get'])
    def Form(self, request):
        fields = self.model._meta.fields + self.model._meta.many_to_many
        fields = list(filter(
            lambda item: item.name in [item for item in
                                       self.get_serializer_class().get_fields(self.get_serializer_class())],
            fields))
        fields = [{"label": item.verbose_name, "field": item.name, "type": fieldDict()[item.get_internal_type()],
                   "inputType": inputFieldDict()[item.get_internal_type()], **dateFormat(item.get_internal_type()),
                   "sortable": True} for item in fields]
        return Response(ColumnsSerializer(fields, many=True).data)

    # @swagger_auto_schema(
    # )
    def retrieve(self, request, pk):
        result = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.get_serializer_class()(result)
        data = serializer.data
        return Response(data)

    @swagger_auto_schema(
        # request_body=serializer_class,
        responses={404: 'not found'}
    )
    def update(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.get_serializer_class()(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        return Response(data)

    @swagger_auto_schema(
        # request_body=serializer_class,
        responses={404: 'not found'}
    )
    def partial_update(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.get_serializer_class()(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        return Response(data)


class AnalysisViewSet(viewsets.ViewSet):
    serializer_class = None
    model = None
    queryset = None
    list_filter_parameter = []
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = []
    filterset_fields = []
    search_fields = []
    modelName = None
    pagination_class = StandardPagination()
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [permissions.IsAuthenticated, ]

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

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        return queryset

    @method_decorator(name='list', decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='columns',
                in_=openapi.IN_QUERY,
                description='columns',
                type=openapi.TYPE_BOOLEAN
            )
        ],
        filter_inspectors=[DjangoFilterDescriptionInspector]
    ))
    def list(self, request):
        print(self.request.user)
        aggregation = self.request.query_params.get('aggregation', False)
        column = self.request.query_params.get('column', False)
        if aggregation:
            result = self.filter_queryset(self.get_queryset())
            totalcount = result.count()
            result = self.pagination_class.paginate_queryset(queryset=result, request=request, view=self)
            serializer = self.get_serializer_class()(result, many=True)
            data = serializer.data
            return Response({"totalCount": totalcount, "result": data})

    # @swagger_auto_schema(
    # )
    def retrieve(self, request, pk):
        result = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.get_serializer_class()(result)
        data = serializer.data
        return Response(data)
