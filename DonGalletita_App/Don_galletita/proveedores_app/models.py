from django.db import models

class Proveedor(models.Model):
    proveedor_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=False)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    dia_entrega = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre
