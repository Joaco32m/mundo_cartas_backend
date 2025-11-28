from django.urls import path
from .views import RegistrarVentaFisicaView

urlpatterns = [
    path("registrar-venta/", RegistrarVentaFisicaView.as_view(), name="registrar-venta-fisica"),
]
