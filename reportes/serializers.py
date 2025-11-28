from rest_framework import serializers
from .models import Venta, DetalleVenta


class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)

    class Meta:
        model = DetalleVenta
        fields = ["producto_nombre", "cantidad", "precio_unitario", "subtotal"]


class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, read_only=True)

    class Meta:
        model = Venta
        fields = ["id", "fecha", "total", "metodo_pago", "detalles"]
