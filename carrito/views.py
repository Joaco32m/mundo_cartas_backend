from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Pedido
from .models import Carrito, ItemCarrito, PedidoItem
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
        cantidad_raw = request.data.get('cantidad', 1)

        if not producto_id:
            return Response({"detail": "producto_id requerido"}, status=status.HTTP_400_BAD_REQUEST)

        # Validar cantidad
        try:
            cantidad = int(cantidad_raw)
            if cantidad < 1:
                raise ValueError()
        except Exception:
            return Response(
                {"detail": "La cantidad debe ser un número entero mayor o igual a 1."},
                status=status.HTTP_400_BAD_REQUEST
            )

        producto = get_object_or_404(Producto, pk=producto_id)
        carrito, _ = Carrito.objects.get_or_create(usuario=perfil)

        # Asegurar stock como entero
        try:
            stock_disponible = int(producto.stock)
        except:
            return Response(
                {"detail": "El stock del producto no es válido. Contacte al administrador."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Buscar si el producto ya está en el carrito
        item = ItemCarrito.objects.filter(carrito=carrito, producto=producto).first()

        # Caso 1: El item ya existe
        if item:
            # Si por error anterior quedó con una cantidad mayor al stock → lo corregimos
            if item.cantidad > stock_disponible:
                item.cantidad = stock_disponible
                item.save()
                return Response(
                    {"detail": f"La cantidad en el carrito era mayor al stock. Se ajustó a {stock_disponible}. Intente nuevamente."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validación: no permitir que la suma total exceda el stock
            if item.cantidad + cantidad > stock_disponible:
                return Response(
                    {"detail": f"Stock insuficiente. Disponible: {stock_disponible}. Ya tienes {item.cantidad} en el carrito."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            item.cantidad += cantidad
            item.save()

        # Caso 2: El item no existe aún
        else:
            if cantidad > stock_disponible:
                return Response(
                    {"detail": f"Stock insuficiente. Disponible: {stock_disponible}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            item = ItemCarrito.objects.create(
                carrito=carrito,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
            )

        serializer = ItemCarritoSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ModificarItem(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, item_id, action):
        perfil = getattr(request.user, 'perfilusuario', None)
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=perfil)

        if action == 'increment':
            if item.cantidad < item.producto.stock:
                item.cantidad += 1
                item.save()
            else:
                return Response(
                    {"detail": "No hay más stock disponible de este producto."},
                    status=status.HTTP_400_BAD_REQUEST
                )

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

        metodo_pago = request.data.get("metodo_pago", "Desconocido")
        direccion = request.data.get("direccion", "")
        cliente_nombre = perfil.user.username

        # IMPORTANTE: Asumimos que todos los productos del carrito pertenecen al mismo vendedor
        vendedor = items.first().producto.vendedor

        # Creamos el pedido
        pedido = Pedido.objects.create(
            vendedor=vendedor,
            cliente=cliente_nombre,
            total=carrito.total(),
            metodo_pago=metodo_pago,
            estado="Pendiente",
        )

        # Crear los items del pedido
        for item in items:
            PedidoItem.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
            )

            # Descontar stock
            item.producto.stock -= item.cantidad
            item.producto.save()

        # Vaciar carrito
        items.delete()

        return Response(PedidoSerializer(pedido).data, status=status.HTTP_201_CREATED)
