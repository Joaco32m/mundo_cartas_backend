from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType

from carrito.models import Carrito, ItemCarrito, Pedido
from .models import TransaccionWebpay

import uuid


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@csrf_exempt
def iniciar_pago(request):

    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "No autenticado"}, status=401)

    perfil = user.perfilusuario

    carrito = perfil.carrito
    items = carrito.items.all()

    if not items.exists():
        return JsonResponse({"error": "Carrito vacío"}, status=400)

    total = carrito.total()

    pedido = Pedido.objects.create(
        vendedor=perfil.user,
        cliente=perfil.user.username,
        total=total,
        metodo_pago="Webpay",
        estado="Pendiente",
    )

    for item in items:
        pedido.productos.add(item.producto)

    buy_order = str(uuid.uuid4())[:12]

    options = WebpayOptions(
        commerce_code="597055555532",
        api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
        integration_type=IntegrationType.TEST,
    )

    tx = Transaction(options)

    try:
        response = tx.create(
            buy_order=buy_order,
            session_id=str(perfil.id),
            amount=float(total),
            return_url="http://127.0.0.1:8000/api/pagos/webpay/confirm/"
        )
    except Exception as e:
        return JsonResponse({"error": f"Error Webpay: {e}"}, status=500)

    TransaccionWebpay.objects.create(
        pedido=pedido,
        token=response["token"],
        orden_compra=buy_order,
        monto=total
    )

    return JsonResponse({
        "url": response["url"],
        "token": response["token"]
    })



@csrf_exempt
def confirmar_pago(request):
    token = request.GET.get("token_ws")

    if not token:
        return JsonResponse({"error": "Token no entregado"}, status=400)

   
    options = WebpayOptions(
        commerce_code="597055555532",
        api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
        integration_type=IntegrationType.TEST,
    )

    tx = Transaction(options)
    resp = tx.commit(token)

    trans = TransaccionWebpay.objects.get(token=token)
    pedido = trans.pedido

   
    if resp["status"] == "AUTHORIZED":
        trans.estado = "AUTORIZADA"
        pedido.estado = "Pagado"

        carrito = pedido.vendedor.perfilusuario.carrito  # Obtener carrito del usuario

        for producto in pedido.productos.all():

            # Buscar el item que corresponde a este producto
            item = carrito.items.get(producto=producto)

            # Restar stock correctamente
            producto.stock -= item.cantidad

            # Evitar valores negativos
            if producto.stock < 0:
                producto.stock = 0

            producto.save()

        pedido.save()
        trans.save()

        # Vaciar carrito
        carrito.items.all().delete()

        return redirect("http://localhost:3000/pago-exitoso")


    
    else:
        trans.estado = "RECHAZADA"
        trans.save()
        return redirect("http://localhost:3000/pago-fallido")
