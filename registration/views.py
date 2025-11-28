from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .serializers import RegistroSerializer, UsuarioCrearActualizarSerializer
from .models import PerfilUsuario, Rol



def validar_rut_chileno(rut):
    if not rut:
        return True

    rut = rut.replace(".", "").replace("-", "").upper()

    if len(rut) < 2:
        return False

    cuerpo = rut[:-1]
    dv = rut[-1]

    if not cuerpo.isdigit():
        return False

    suma = 0
    multiplicador = 2

    for c in reversed(cuerpo):
        suma += int(c) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resto = suma % 11
    dv_esperado = 11 - resto

    if dv_esperado == 11:
        dv_esperado = "0"
    elif dv_esperado == 10:
        dv_esperado = "K"
    else:
        dv_esperado = str(dv_esperado)

    return dv == dv_esperado



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    return Response({
        "username": request.user.username,
        "email": request.user.email,
        "rol": perfil.rol.nombre,
        "rut": perfil.rut,
        "telefono": perfil.telefono
    })



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
                "rol": perfil.rol.nombre
            }, status=201)

        return Response(serializer.errors, status=400)


class UsuarioCRUDAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _es_admin(self, request):
        return PerfilUsuario.objects.get(user=request.user).rol.nombre == "Administrador"


    def get(self, request):
        if not self._es_admin(request):
            return Response({"error": "No tienes permisos"}, status=403)

        usuarios = User.objects.all()
        data = []

        for u in usuarios:
            perfil = PerfilUsuario.objects.filter(user=u).first()
            data.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "rut": perfil.rut if perfil else "",
                "telefono": perfil.telefono if perfil else "",
                "rol": perfil.rol.nombre if perfil else "Sin perfil"
            })

        return Response(data)


    def post(self, request):
        if not self._es_admin(request):
            return Response({"error": "No tienes permisos"}, status=403)

        serializer = UsuarioCrearActualizarSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        rut = data.get("rut", "")


        if rut and not validar_rut_chileno(rut):
            return Response({"error": "El RUT ingresado no es válido"}, status=400)

        if rut and PerfilUsuario.objects.filter(rut=rut).exists():
            return Response({"error": "El RUT ya está registrado"}, status=400)

        try:
            user = User(username=data["username"], email=data["email"])

            user._crear_como_empleado = True

            if data.get("password"):
                user.set_password(data["password"])
            else:
                user.set_password(User.objects.make_random_password())

            user.full_clean()
            user.save()

        except ValidationError as e:
            return Response({"error": list(e.message_dict.values())[0][0]}, status=400)

        try:
            rol_obj = Rol.objects.get(nombre=data["rol"])
        except Rol.DoesNotExist:
            return Response({"error": "Rol inválido"}, status=400)

        PerfilUsuario.objects.update_or_create(
            user=user,
            defaults={
                "rol": rol_obj,
                "rut": rut,
                "telefono": data.get("telefono", "")
            }
        )

        return Response({"message": "Usuario creado correctamente"}, status=201)

    def put(self, request, id=None):
        if not self._es_admin(request):
            return Response({"error": "No tienes permisos"}, status=403)

        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

        serializer = UsuarioCrearActualizarSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        rut = data.get("rut", "")

        if rut and not validar_rut_chileno(rut):
            return Response({"error": "El RUT ingresado no es válido"}, status=400)

        if rut and PerfilUsuario.objects.filter(rut=rut).exclude(user=user).exists():
            return Response({"error": "Otro usuario ya tiene ese RUT"}, status=400)

        user.username = data["username"]
        user.email = data["email"]

        if data.get("password"):
            user.set_password(data["password"])

        try:
            user.full_clean()
            user.save()
        except ValidationError as e:
            return Response({"error": list(e.message_dict.values())[0][0]}, status=400)


        perfil, _ = PerfilUsuario.objects.get_or_create(user=user)

        perfil.rut = rut
        perfil.telefono = data.get("telefono", "")

        try:
            rol_obj = Rol.objects.get(nombre=data["rol"])
        except Rol.DoesNotExist:
            return Response({"error": "Rol inválido"}, status=400)

        perfil.rol = rol_obj
        perfil.save()

        return Response({"message": "Usuario actualizado correctamente"}, status=200)


    def delete(self, request, id=None):
        if not self._es_admin(request):
            return Response({"error": "No tienes permisos"}, status=403)

        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

        user.delete()
        return Response({"message": "Usuario eliminado correctamente"}, status=200)
