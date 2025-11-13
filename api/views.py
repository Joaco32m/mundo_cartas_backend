from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Producto, Pedido
from .serializers import ProductoSerializer, PedidoSerializer
from registration.permissions import EsVendedor, EsAdmin


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_permissions(self):
        """
        - Cualquiera puede ver los productos (GET, list, retrieve)
        - Solo administradores pueden crear, actualizar o eliminar
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [EsAdmin]
        return [permission() for permission in permission_classes]


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, 'perfilusuario', None)

        if perfil and perfil.rol.nombre == "Vendedor":
            return Pedido.objects.filter(vendedor=user).order_by('-fecha')

        elif perfil and perfil.rol.nombre == "Administrador":
            return Pedido.objects.all().order_by('-fecha')

        return Pedido.objects.none()

    def perform_create(self, serializer):
        serializer.save(vendedor=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_usuario_actual(request):
    """
    Devuelve los datos del usuario autenticado, incluyendo su rol.
    """
    user = request.user
    perfil = getattr(user, 'perfilusuario', None)
    rol = perfil.rol.nombre if perfil and perfil.rol else "Cliente"

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "rol": rol
    })
