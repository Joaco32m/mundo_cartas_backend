from django.db import models
from django.conf import settings
from api.models import Producto

class VentaFisica(models.Model):
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ventas_fisicas"
    )
    cliente = models.CharField(max_length=100, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Venta #{self.id} - {self.vendedor.username}"


class VentaFisicaItem(models.Model):
    venta = models.ForeignKey(
        VentaFisica,
        on_delete=models.CASCADE,
        related_name="items"
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
