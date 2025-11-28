from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PerfilUsuario, Rol


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

        return user


class UsuarioSerializer(serializers.ModelSerializer):
    rut = serializers.CharField(
        source='perfilusuario.rut', allow_blank=True, allow_null=True
    )
    telefono = serializers.CharField(
        source='perfilusuario.telefono', allow_blank=True, allow_null=True
    )
    rol = serializers.CharField(source='perfilusuario.rol.nombre')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'rut', 'telefono', 'rol']


class UsuarioCrearActualizarSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(required=False, write_only=True, allow_blank=True)
    rut = serializers.CharField(required=False, allow_blank=True)
    telefono = serializers.CharField(required=False, allow_blank=True)
    rol = serializers.CharField()

    def validate_rol(self, value):
        value = value.strip()
        if not Rol.objects.filter(nombre=value).exists():
            raise serializers.ValidationError("Rol inválido")
        return value

    def validate_username(self, value):
        if " " in value:
            raise serializers.ValidationError("El usuario no debe contener espacios")
        return value

    def validate(self, data):
        if data.get("password", "") == "":
            data.pop("password", None)
        return data
