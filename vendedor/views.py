from rest_framework import generics, permissions
from rest_framework.response import Response
from .serializers import RegistrarVentaFisicaSerializer, VentaFisicaSerializer

class RegistrarVentaFisicaView(generics.CreateAPIView):
    serializer_class = RegistrarVentaFisicaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        venta = serializer.save()

        respuesta = VentaFisicaSerializer(venta).data  

        return Response(respuesta, status=201)
