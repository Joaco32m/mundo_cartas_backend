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
    ESTADOS = [
        ("Pendiente", "Pendiente"),
        ("Enviado", "Enviado"),
        ("Entregado", "Entregado"),
        ("Cancelado", "Cancelado"),
    ]

    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pedidos_vendedor"
    )
    cliente = models.CharField(max_length=100)
    productos = models.ManyToManyField(Producto, related_name="pedidos")
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="Pendiente")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.vendedor.username} ({self.estado})"
    
class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
