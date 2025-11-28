from django.db import models
from api.models import Producto
from registration.models import PerfilUsuario


class Venta(models.Model):
    usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.CharField(max_length=50, default="WebPay")  

    def __str__(self):
        return f"Venta #{self.id} - {self.usuario.user.username}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name="detalles", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
