from django.db import models

# Create your models here.
class Producto(models.Model):
    producto_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    unidad_medida = models.CharField(max_length=3, choices=[
        ('kg', 'Kilogramos'), 
        ('g', 'Gramos'), 
        ('pz', 'Piezas')
    ])
    cantidad_disponible = models.IntegerField(default=0)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    peso_unidad = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_caducidad = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.nombre