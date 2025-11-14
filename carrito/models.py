from django.db import models
from django.conf import settings
from registration.models import PerfilUsuario 
from api.models import Producto
from django.utils import timezone

class Carrito(models.Model):
    usuario = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE, related_name='carrito')
    creado = models.DateTimeField(auto_now_add=True)

    def total(self):
        total = 0
        for item in self.items.all():            
            total += item.subtotal()
        return total

    def __str__(self):
        return f"Carrito de {self.usuario.user.username}"


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
       
        try:
            return self.cantidad * self.precio_unitario
        except Exception:
            return self.cantidad * 0

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


class Pedido(models.Model):
    usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    ESTADOS = [
        ('PEND', 'Pendiente'),
        ('CONF', 'Confirmado'),
        ('CANC', 'Cancelado'),
    ]
    estado = models.CharField(max_length=4, choices=ESTADOS, default='PEND')

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.user.username}"