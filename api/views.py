from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from carrito.models import Pedido
from .models import Producto, Categoria
from .serializers import ProductoSerializer, CategoriaSerializer
from carrito.serializers import PedidoSerializer
from registration.permissions import EsVendedor, EsAdmin


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [EsAdmin()]
    
    def get_serializer_context(self):
        return {"request": self.request}
    
    
    def get_queryset(self):
        qs = Producto.objects.all()

        nombre = self.request.query_params.get("nombre")
        categoria = self.request.query_params.get("categoria")

        if nombre:
            qs = qs.filter(nombre__icontains=nombre)

        if categoria:
            qs = qs.filter(categoria__iexact=categoria)

        return qs
    
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [EsAdmin()]


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, 'perfilusuario', None)

        if perfil and perfil.rol.nombre in ["Vendedor", "Administrador"]:
            return Pedido.objects.all().order_by('-fecha')

        return Pedido.objects.none()

    def perform_create(self, serializer):
        serializer.save(vendedor=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_usuario_actual(request):
    user = request.user
    perfil = getattr(user, 'perfilusuario', None)
    rol = perfil.rol.nombre if perfil and perfil.rol else "Cliente"

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "rol": rol
    })
