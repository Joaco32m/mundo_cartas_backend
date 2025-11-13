from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistroSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import PerfilUsuario

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    data = {
        "username": request.user.username,
        "email": request.user.email,
        "rol": perfil.rol.nombre
    }
    return Response(data)


class RegistroAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Usuario creado correctamente 🎉",
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PerfilAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        perfil = PerfilUsuario.objects.get(user=request.user)
        return Response({
            "username": request.user.username,
            "email": request.user.email,
            "rol": perfil.rol.nombre
        })