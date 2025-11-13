from rest_framework import serializers
from .models import Producto, Pedido


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


class PedidoSerializer(serializers.ModelSerializer):
    productos = ProductoSerializer(many=True, read_only=True)
    vendedor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Pedido
        fields = '__all__'
