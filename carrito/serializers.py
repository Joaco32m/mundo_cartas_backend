from rest_framework import serializers
from api.models import Pedido
from .models import Carrito, ItemCarrito
from api.serializers import ProductoSerializer
from api.models import Producto

class ItemCarritoSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())

    producto_detalle = serializers.SerializerMethodField()

    class Meta:
        model = ItemCarrito
        fields = ['id', 'producto', 'producto_detalle', 'cantidad','precio_unitario','subtotal']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        from api.models import Producto
        from api.serializers import ProductoSerializer as ProdSer
        self.fields['producto'].queryset = Producto.objects.all()
        self._prod_serializer = ProdSer

    def get_producto_detalle(self, obj):
        return self._prod_serializer(obj.producto).data

    subtotal = serializers.SerializerMethodField()
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


class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['id', 'usuario', 'fecha', 'total', 'estado']
        read_only_fields = ['fecha', 'estado']