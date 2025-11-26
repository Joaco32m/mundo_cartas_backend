from rest_framework import serializers
from .models import Pedido, Carrito, ItemCarrito, PedidoItem
from api.serializers import ProductoSerializer
from api.models import Producto


class ItemCarritoSerializer(serializers.ModelSerializer):
    
    producto = ProductoSerializer(read_only=True)

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemCarrito
        fields = [
            'id',
            'producto',
            'cantidad',
            'precio_unitario',
            'subtotal'
        ]

    def get_subtotal(self, obj):
        return obj.subtotal()


class CarritoSerializer(serializers.ModelSerializer):
    items = ItemCarritoSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carrito
        fields = ['id', 'usuario', 'creado', 'items', 'total']
        read_only_fields = ['usuario', 'creado', 'items', 'total']

    def get_total(self, obj):
        return obj.total()


class PedidoItemSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source="producto.nombre")
    precio = serializers.IntegerField(source="precio_unitario")

    class Meta:
        model = PedidoItem
        fields = ["nombre", "cantidad", "precio"]


class PedidoSerializer(serializers.ModelSerializer):
    productos = PedidoItemSerializer(source="items", many=True)
    vendedor = serializers.CharField(source="vendedor.username")

    class Meta:
        model = Pedido
        fields = [
            "id", "cliente", "direccion", "metodo_pago", "estado", "fecha",
            "productos", "total", "vendedor"
        ]
