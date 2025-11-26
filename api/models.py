from django.db import models
from django.conf import settings


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=100, default="Sin categoría")
    stock = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/')

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    def __str__(self):
        return self.nombre


