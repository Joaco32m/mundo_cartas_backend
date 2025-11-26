from django.db import models
from carrito.models import Pedido
from django.utils import timezone
# Create your models here.


class TransaccionWebpay(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='transaccion')
    token = models.CharField(max_length=255, unique=True)
    orden_compra = models.CharField(max_length=100, unique=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    estado = models.CharField(
        max_length=20,
        default="INICIADA"
    )

    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Transacción {self.orden_compra} - {self.estado}"
