from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from carrito.models import Pedido


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resumen_vendedor(request):

    pedidos = Pedido.objects.all()

    total_ventas = pedidos.count()
    ingresos_total = sum([p.total for p in pedidos])

    data = {
        "totalVentas": total_ventas,
        "ingresos": ingresos_total,
    }

    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pedidos_vendedor(request):

    pedidos = Pedido.objects.all().order_by('-fecha')

    serialized = []
    for p in pedidos:
        serialized.append({
            "id": p.id,
            "cliente": p.cliente,
            "total": p.total,
            "estado": p.estado,
            "metodo_pago": p.metodo_pago,
            "fecha": p.fecha,
            "productos": [
                {
                    "nombre": prod.nombre,
                    "precio": prod.precio,
                    "cantidad": 1  #
                }
                for prod in p.productos.all()
            ]
        })

    return Response(serialized)
