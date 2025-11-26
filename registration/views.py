from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistroSerializer, UsuarioCrearActualizarSerializer, UsuarioSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import PerfilUsuario, Rol
from django.contrib.auth.models import User


# ========== PERFIL DEL USUARIO LOGEADO ==========
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    data = {
        "username": request.user.username,
        "email": request.user.email,
        "rol": perfil.rol.nombre,
        "rut": perfil.rut,
        "telefono": perfil.telefono,
    }
    return Response(data)



# ========== REGISTRO NORMAL (CLIENTE) ==========
class RegistroAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            perfil = PerfilUsuario.objects.get(user=user)

            return Response({
                "message": "Registro exitoso",
                "username": user.username,
                "email": user.email,
                "rol": perfil.rol.nombre  # debe ser Cliente
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ========== PERFIL PRIVADO ==========
class PerfilAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        perfil = PerfilUsuario.objects.get(user=request.user)
        return Response({
            "username": request.user.username,
            "email": request.user.email,
            "rol": perfil.rol.nombre,
            "rut": perfil.rut,
            "telefono": perfil.telefono
        })



# ========== CRUD COMPLETO DE USUARIOS ==========
class UsuarioCRUDAPIView(APIView):

    # LISTAR
    def get(self, request):
        usuarios = User.objects.all()
        data = []
        for user in usuarios:
            perfil = PerfilUsuario.objects.get(user=user)
            data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "rut": perfil.rut or "",
                "telefono": perfil.telefono or "",
                "rol": perfil.rol.nombre
            })
        return Response(data)

    # CREAR (SOLO ADMIN)
    def post(self, request):
        serializer = UsuarioCrearActualizarSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data

        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"]
        )

        perfil = PerfilUsuario.objects.get(user=user)

        # Asignar rol ESPECÍFICO (Admin o Vendedor)
        rol_obj = Rol.objects.get(nombre=data["rol"])
        perfil.rol = rol_obj

        perfil.rut = data.get("rut", "")
        perfil.telefono = data.get("telefono", "")
        perfil.save()

        return Response({"message": "Usuario creado correctamente"}, status=201)

    # EDITAR
    def put(self, request, id=None):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

        serializer = UsuarioCrearActualizarSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data

        # Actualizar campos de usuario
        user.username = data["username"]
        user.email = data["email"]
        if data.get("password"):
            user.set_password(data["password"])
        user.save()

        # Actualizar perfil
        perfil = PerfilUsuario.objects.get(user=user)
        perfil.rut = data.get("rut", "")
        perfil.telefono = data.get("telefono", "")

        rol_obj = Rol.objects.get(nombre=data["rol"])
        perfil.rol = rol_obj
        perfil.save()

        return Response({"message": "Usuario actualizado correctamente"})

    # ELIMINAR
    def delete(self, request, id=None):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

        user.delete()
        return Response({"message": "Usuario eliminado correctamente"})
