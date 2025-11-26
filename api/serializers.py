from rest_framework import serializers
from .models import Producto,Categoria

class ProductoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ["id", "nombre", "descripcion", "precio", "categoria", "stock", "imagen", "imagen_url"]

    def get_imagen_url(self, obj):
        request = self.context.get("request")

        if obj.imagen:
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url  # fallback sin request

        return None


    
class CategoriaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Categoria
        fields = "__all__"