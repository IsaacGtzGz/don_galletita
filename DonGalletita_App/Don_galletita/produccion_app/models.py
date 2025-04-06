from django.db import models
from recetas_app.models import Receta
from insumos_app.models import Insumos
from usuarios_app.models import Usuario
from django.core.exceptions import ValidationError
from django.utils.timezone import now

# Create your models here.
class Produccion(models.Model):
    produccion_id = models.AutoField(primary_key=True)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    cantidad_producida = models.PositiveIntegerField(default=0)  # Se calculará a partir de la receta
    
    def calcular_cantidad_producida(self):
        """Calcula la cantidad total de galletas producidas basado en la receta."""
        return self.receta.porciones_galletas
    
    def save(self, *args, **kwargs):
        if not self.fecha_inicio:
            self.fecha_inicio = now()

        if self.fecha_finalizacion and self.fecha_inicio and self.fecha_finalizacion < self.fecha_inicio:
            raise ValidationError("La fecha de finalización no puede ser anterior a la fecha de inicio.")

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Producción {self.produccion_id} - {self.receta.nombre}"

class LoteProduccion(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible para venta'),
        ('por_caducar', 'Próximo a caducar'),
        ('caducado', 'Caducado (merma)'),
    ]
    
    lote_id = models.AutoField(primary_key=True)
    produccion = models.ForeignKey(Produccion, on_delete=models.CASCADE)
    cantidad_galletas = models.PositiveIntegerField()
    fecha_caducidad = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    
    def __str__(self):
        return f"Lote {self.lote_id} - {self.produccion.receta.producto.nombre} (Cad: {self.fecha_caducidad})"
    
    class Meta:
        verbose_name = "Lote de Producción"
        verbose_name_plural = "Lotes de Producción"
        ordering = ['fecha_caducidad']

class ConsumoInsumos(models.Model):
    consumo_id = models.AutoField(primary_key=True) 
    produccion = models.ForeignKey(Produccion, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumos, on_delete=models.CASCADE)
    cantidad_usada = models.DecimalField(max_digits=10, decimal_places=3)
    
    def __str__(self):
        return f"Consumo {self.insumo.nombre_insumo} ({self.cantidad_usada})"