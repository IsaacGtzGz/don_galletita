from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import os

# Create your models here.
def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.png', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Formatos soportados: JPG, PNG, JPEG')
    
class Producto(models.Model):
    producto_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    unidad_medida = models.CharField(
        max_length=3, 
        choices=[('pz', 'Piezas')],  # Solo una opción disponible
        default='pz'  # Valor por defecto
    )
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    peso_unidad = models.DecimalField(max_digits=5, decimal_places=2)
    imagen_producto = models.ImageField(upload_to='productos/', blank=True, null=True)  

    imagen_producto = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True,
        validators=[validate_image_extension]
    )

    def save(self, *args, **kwargs):
        if self.cantidad_disponible < 0:
            raise ValueError("La cantidad disponible no puede ser negativa.")
        self.full_clean()
        super().save(*args, **kwargs)

    def fecha_caducidad_proxima(self):
        """Obtiene la fecha de caducidad más próxima de los lotes disponibles"""
        from produccion_app.models import LoteProduccion  # Importación local para evitar circular
        lote = LoteProduccion.objects.filter(
            produccion__receta__producto=self,
            estado='disponible'
        ).order_by('fecha_caducidad').first()
        return lote.fecha_caducidad if lote else None
    
    def cantidad_por_caducar(self, dias=2):
        """Obtiene la cantidad que caducará en los próximos X días"""
        from produccion_app.models import LoteProduccion
        fecha_limite = timezone.now().date() + timedelta(days=dias)
        lotes = LoteProduccion.objects.filter(
            produccion__receta__producto=self,
            fecha_caducidad__lte=fecha_limite,
            estado='disponible'
        )
        return sum(lote.cantidad_galletas for lote in lotes)

    def __str__(self):
        return self.nombre