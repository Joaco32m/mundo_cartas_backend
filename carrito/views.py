from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from api.models import Pedido
from .models import Carrito, ItemCarrito
from .serializers import CarritoSerializer, ItemCarritoSerializer, PedidoSerializer
from api.models import Producto 
from registration.models import PerfilUsuario

class CarritoDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_perfil(self, request):
        perfil = getattr(request.user, 'perfilusuario', None)
        if not perfil:
            perfil = get_object_or_404(PerfilUsuario, usuario=request.user)
        return perfil

    def get(self, request):
        perfil = self.get_perfil(request)
        carrito, _ = Carrito.objects.get_or_create(usuario=perfil)
        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)


class AgregarAlCarrito(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        perfil = getattr(request.user, 'perfilusuario', None)
        if not perfil:
            return Response({"detail": "Perfil no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))

        if not producto_id:
            return Response({"detail": "producto_id requerido"}, status=status.HTTP_400_BAD_REQUEST)

        producto = get_object_or_404(Producto, pk=producto_id)
        carrito, _ = Carrito.objects.get_or_create(usuario=perfil)

        item, creado = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={
                "cantidad": cantidad,
                "precio_unitario": producto.precio,
            }
        )

        if not creado:
            item.cantidad += cantidad
            item.save()

        serializer = ItemCarritoSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class ModificarItem(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, item_id, action):
        perfil = getattr(request.user, 'perfilusuario', None)
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=perfil)

        if action == 'increment':
            item.cantidad += 1
            item.save()
        elif action == 'decrement':
            if item.cantidad > 1:
                item.cantidad -= 1
                item.save()
            else:
                item.delete()
                return Response({"detail": "Item eliminado"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Accion inválida"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ItemCarritoSerializer(item).data)


class EliminarItem(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        perfil = getattr(request.user, 'perfilusuario', None)
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=perfil)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Checkout(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        perfil = getattr(request.user, 'perfilusuario', None)
        carrito = get_object_or_404(Carrito, usuario=perfil)
        items = carrito.items.all()
        if not items.exists():
            return Response({"detail": "Carrito vacío"}, status=status.HTTP_400_BAD_REQUEST)

        total = carrito.total()
        pedido = Pedido.objects.create(usuario=perfil, total=total, estado='CONF')
        items.delete()
        serializer = PedidoSerializer(pedido)
        return Response(serializer.data, status=status.HTTP_201_CREATED)