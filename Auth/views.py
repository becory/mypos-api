from django.contrib.auth.models import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.views import TokenVerifyView
from Auth.serializers import POSTokenVerifySerializer, UserSerializer, UserCreateSerializer

# Create your views here.
from patches.viewset import BasicViewSet


class IsAdminSuperUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff and request.user.is_superuser)


class UserViewSet(BasicViewSet):
    model = User
    queryset = model.objects.all()
    serializer_class = UserSerializer
    create_serializer_class = UserCreateSerializer
    update_serializer_class = UserCreateSerializer
    partial_update_serializer_class = UserCreateSerializer
    filterset_fields = ['first_name', 'last_name', 'email', 'password', 'username', 'is_staff', 'is_superuser']
    ordering_fields = ['name', 'itemType', 'startDate', 'endDate', 'week']
    search_fields = ['name', 'itemType', 'startDate', 'endDate', 'week']
    modelName = User.__name__
    permission_classes = [IsAdminSuperUser]

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



@authentication_classes([])
@permission_classes([])
class POSTokenVerifyView(TokenVerifyView):
    serializer_class = POSTokenVerifySerializer
