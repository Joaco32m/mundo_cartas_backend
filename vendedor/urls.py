from django.urls import path
from .views import resumen_vendedor, pedidos_vendedor

urlpatterns = [
    path("resumen/", resumen_vendedor),
    path("pedidos/", pedidos_vendedor),
]
