from rest_framework import routers
from django.urls import path, include
from .views import ProductoViewSet, PedidoViewSet, CategoriaViewSet ,obtener_usuario_actual

router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'categorias', CategoriaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('usuarios/me/', obtener_usuario_actual),
]
