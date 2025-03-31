from django.db import models
from insumos_app.models import Insumos

UNIDADES_CHOICES = (
    ('kg', 'Kilogramos'),
    ('g', 'Gramos'),
    ('ml', 'Mililitros'),
    ('l', 'Litros'),
    ('pz', 'Piezas'),
)

class Recetas(models.Model):
    nombre_receta = models.CharField(max_length=200, default="Receta sin nombre")
    foto_receta = models.ImageField(upload_to='recetas/', null=True, blank=True)
    preparacion = models.TextField(default="Sin descripción")
    porciones_galletas = models.IntegerField(default=1)
 
    def __str__(self):
        return f"{self.receta_id}-{self.nombre_receta}-{self.foto_receta}-{self.preparacion}-{self.porciones_galletas}"


class RecetaInsumo(models.Model):
    receta = models.ForeignKey(Recetas, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumos, on_delete=models.CASCADE)
    cantidad_necesaria = models.DecimalField(max_digits=10, decimal_places=3)
    unidad_medida = models.CharField(max_length=10, choices=Insumos.UNIDADES_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.receta.nombre_receta}-{self.insumo.nombre_insumo}-{self.cantidad_necesaria}-{self.unidad_medida}"