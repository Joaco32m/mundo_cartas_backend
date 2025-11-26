from rest_framework import serializers
from .models import Producto,Categoria

class ProductoSerializer(serializers.ModelSerializer):
    imagen = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = "__all__"

    def get_imagen(self, obj):
        if obj.imagen:
            return obj.imagen.url
        return None
    
    
class CategoriaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Categoria
        fields = "__all__"