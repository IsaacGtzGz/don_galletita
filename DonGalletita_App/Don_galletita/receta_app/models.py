from django.db import models
from insumos_app.models import Insumos
from productos_app.models import Producto

UNIDADES_CHOICES = (
    ('kg', 'Kilogramos'),
    ('g', 'Gramos'),
    ('ml', 'Mililitros'),
    ('l', 'Litros'),
    ('pz', 'Piezas'),
)

class Receta(models.Model):
    receta_id = models.AutoField(primary_key=True)
    producto = producto = models.ForeignKey(Producto, on_delete=models.CASCADE, )
    foto_receta = models.ImageField(upload_to='recetas/', null=True, blank=True)
    preparacion = models.TextField(default="Sin descripción")
    porciones_galletas = models.IntegerField(default=1)
 
    def _str_(self):
        return f"Receta para {self.producto.nombre} (ID: {self.receta_id})"


class RecetaInsumo(models.Model):
    recetasinsumo_id = models.AutoField(primary_key=True)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumos, on_delete=models.CASCADE)
    cantidad_necesaria = models.IntegerField(default=0)
    unidad_medida = models.CharField(max_length=10, choices=Insumos.UNIDADES_CHOICES, null=True, blank=True)

    def _str_(self):
        return f"{self.receta.producto.nombre}-{self.insumo.nombre_insumo}-{self.cantidad_necesaria}-{self.unidad_medida}"