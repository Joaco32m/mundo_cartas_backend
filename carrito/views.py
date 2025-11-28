from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Pedido, Carrito, ItemCarrito, PedidoItem
from .serializers import CarritoSerializer, ItemCarritoSerializer, PedidoSerializer
from api.models import Producto
from registration.models import PerfilUsuario
from reportes.models import Venta


def get_or_create_perfil(user):
    perfil = getattr(user, 'perfilusuario', None)
    if not perfil:
        perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
    return perfil


class CarritoDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        perfil = get_or_create_perfil(request.user)
        carrito, _ = Carrito.objects.get_or_create(usuario=perfil)
        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)


class AgregarAlCarrito(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        perfil = get_or_create_perfil(request.user)

        producto_id = request.data.get('producto_id')
        cantidad_raw = request.data.get('cantidad', 1)

        if not producto_id:
            return Response({"detail": "producto_id requerido"}, status=400)

        try:
            cantidad = int(cantidad_raw)
            if cantidad < 1:
                raise ValueError()
        except:
            return Response({"detail": "Cantidad inválida"}, status=400)

        producto = get_object_or_404(Producto, pk=producto_id)
        carrito, _ = Carrito.objects.get_or_create(usuario=perfil)

        stock_disponible = int(producto.stock)
        item = ItemCarrito.objects.filter(carrito=carrito, producto=producto).first()

        if item:

            if item.cantidad >= stock_disponible:
                return Response(
                    {"ok": False, "detail": "Stock máximo alcanzado"},
                    status=400
                )
            if item.cantidad + cantidad > stock_disponible:
                return Response(
                    {"ok": False, "detail": f"Solo quedan {stock_disponible - item.cantidad} disponibles"},
                    status=400
                )

            item.cantidad += cantidad
            item.save()

            return Response({"ok": True, "item": ItemCarritoSerializer(item).data}, status=200)

        if cantidad > stock_disponible:
            return Response(
                {"ok": False, "detail": f"Solo {stock_disponible} disponibles"},
                status=400
            )

        item = ItemCarrito.objects.create(
            carrito=carrito,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio
        )

        return Response({"ok": True, "item": ItemCarritoSerializer(item).data}, status=201)


class ModificarItem(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, item_id, action):
        perfil = get_or_create_perfil(request.user)
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=perfil)

        stock_disponible = int(item.producto.stock)

        if action == 'increment':
            if item.cantidad < stock_disponible:
                item.cantidad += 1
                item.save()
            else:
                return Response({"detail": "No hay más stock disponible."}, status=200)

        elif action == 'decrement':
            if item.cantidad > 1:
                item.cantidad -= 1
                item.save()
            else:
                item.delete()
                return Response({"detail": "Item eliminado"}, status=200)

        else:
            return Response({"detail": "Acción inválida"}, status=400)

        return Response(ItemCarritoSerializer(item).data)


class EliminarItem(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        perfil = get_or_create_perfil(request.user)
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=perfil)
        item.delete()
        return Response(status=204)


class CheckoutCliente(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        perfil = get_or_create_perfil(request.user)
        carrito = get_object_or_404(Carrito, usuario=perfil)
        items = carrito.items.all()

        if not items.exists():
            return Response({"detail": "Carrito vacío"}, status=400)

        for item in items:
            if item.producto.vendedor is None:
                return Response(
                    {"detail": f"El producto '{item.producto.nombre}' no tiene vendedor asignado."},
                    status=500
                )

        vendedor = items.first().producto.vendedor

        pedido = Pedido.objects.create(
            vendedor=vendedor,
            cliente=perfil.user.username,
            total=carrito.total(),
            metodo_pago="Webpay",
            estado="Pendiente"
        )

        for item in items:
            PedidoItem.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario
            )
            item.producto.stock -= item.cantidad
            item.producto.save()

        Venta.objects.create(
            usuario=perfil.user,
            fecha=pedido.fecha,
            total=carrito.total(),
            metodo_pago="Webpay"
        )

        items.delete()

        return Response(PedidoSerializer(pedido).data, status=201)


class CheckoutVendedor(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        vendedor = request.user

        productos = request.data.get("items", [])
        cliente = request.data.get("cliente", "Cliente presencial")
        metodo_pago = request.data.get("metodo_pago", "Efectivo")

        if not productos:
            return Response({"detail": "No hay productos"}, status=400)

        total = 0
        pedido = Pedido.objects.create(
            vendedor=vendedor,
            cliente=cliente,
            total=0,
            metodo_pago=metodo_pago,
            estado="Completado"
        )

        for item in productos:
            producto = Producto.objects.get(id=item["producto_id"])
            cantidad = int(item["cantidad"])

            PedidoItem.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )

            producto.stock -= cantidad
            producto.save()

            total += producto.precio * cantidad

        pedido.total = total
        pedido.save()

        Venta.objects.create(
            usuario=vendedor,
            total=total,
            metodo_pago=metodo_pago,
            fecha=pedido.fecha
        )

        return Response(PedidoSerializer(pedido).data, status=201)
