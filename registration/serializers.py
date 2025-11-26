from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PerfilUsuario, Rol


# ========== REGISTRO DE CLIENTE ==========
class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        # Rol = Cliente automáticamente por la señal
        return user



# ========== LECTURA DE USUARIOS PARA EL CRUD ==========
class UsuarioSerializer(serializers.ModelSerializer):
    rut = serializers.CharField(source='perfilusuario.rut', allow_blank=True, allow_null=True)
    telefono = serializers.CharField(source='perfilusuario.telefono', allow_blank=True, allow_null=True)
    rol = serializers.CharField(source='perfilusuario.rol.nombre')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'rut', 'telefono', 'rol']



# ========== CRUD DE EMPLEADOS ==========
class UsuarioCrearActualizarSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(required=False, write_only=True)
    rut = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    telefono = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    rol = serializers.CharField(required=True)

    def validate_rol(self, value):
        if not Rol.objects.filter(nombre=value).exists():
            raise serializers.ValidationError("Rol inválido")
        return value
