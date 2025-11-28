from rest_framework import serializers
from api.models import Producto
from .models import VentaFisica, VentaFisicaItem


class VentaFisicaItemSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)

    class Meta:
        model = VentaFisicaItem
        fields = [
            "producto",
            "producto_nombre",
            "cantidad",
            "precio_unitario",
            "subtotal"
        ]


class VentaFisicaSerializer(serializers.ModelSerializer):
    items = VentaFisicaItemSerializer(many=True, read_only=True)

    class Meta:
        model = VentaFisica
        fields = [
            "id",
            "vendedor",
            "cliente",
            "fecha",
            "metodo_pago",
            "total",
            "items"
        ]


class RegistrarVentaFisicaSerializer(serializers.Serializer):
    cliente = serializers.CharField(required=False, allow_blank=True)
    metodo_pago = serializers.CharField()
    items = serializers.ListSerializer(child=serializers.DictField())

    def validate(self, data):
        items = data["items"]

        if not items:
            raise serializers.ValidationError("Debe incluir al menos un producto.")

        for item in items:
            if "producto_id" not in item or "cantidad" not in item:
                raise serializers.ValidationError(
                    "Falta producto_id o cantidad en un item."
                )

            try:
                producto = Producto.objects.get(id=item["producto_id"])
            except Producto.DoesNotExist:
                raise serializers.ValidationError(
                    f"Producto con ID {item['producto_id']} no existe."
                )

            if producto.stock < item["cantidad"]:
                raise serializers.ValidationError(
                    f"Stock insuficiente para {producto.nombre}."
                )

        return data

    def create(self, validated_data):
        vendedor = self.context["request"].user
        metodo_pago = validated_data["metodo_pago"]
        cliente = validated_data.get("cliente", "") or "Cliente presencial"
        items = validated_data["items"]

        venta = VentaFisica.objects.create(
            vendedor=vendedor,
            metodo_pago=metodo_pago,
            cliente=cliente
        )

        total = 0

        for item in items:
            producto = Producto.objects.get(id=item["producto_id"])
            cantidad = int(item["cantidad"])

            subtotal = producto.precio * cantidad
            total += subtotal

            VentaFisicaItem.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
                subtotal=subtotal
            )

            producto.stock -= cantidad
            producto.save()

        venta.total = total
        venta.save()

        return venta
