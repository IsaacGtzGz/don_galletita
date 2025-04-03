from django.db import models
from productos_app.models import Producto
from insumos_app.models import Insumos

# Create your models here.
class Produccion(models.Model):
    produccion_id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    cantidad_producida = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Producción {self.produccion_id} - {self.producto.nombre}"

class LoteProduccion(models.Model):
    lote_id = models.AutoField(primary_key=True)
    produccion = models.ForeignKey(Produccion, on_delete=models.CASCADE)
    cantidad_galletas = models.PositiveIntegerField()
    fecha_caducidad = models.DateField()
    
    def __str__(self):
        return f"Lote {self.lote_id} - {self.produccion.producto.nombre} ({self.cantidad_galletas} piezas)"

class ConsumoInsumos(models.Model):
    consumo_id = models.AutoField(primary_key=True) 
    produccion = models.ForeignKey(Produccion, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumos, on_delete=models.CASCADE)
    cantidad_usada = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Consumo {self.insumo.nombre_insumo} ({self.cantidad_usada})"