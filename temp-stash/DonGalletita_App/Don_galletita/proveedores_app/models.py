from django.db import models

class Proveedor(models.Model):
    proveedor_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, null=False)
    apellido_paterno = models.CharField(max_length=255, null=False)
    apellido_materno = models.CharField(max_length=255, null=False)
    telefono = models.CharField(max_length=10, null=False)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"
