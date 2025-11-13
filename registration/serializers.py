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

        rol, _ = Rol.objects.get_or_create(nombre="Cliente")
        
        PerfilUsuario.objects.create(user=user, rol=rol)

        return user
