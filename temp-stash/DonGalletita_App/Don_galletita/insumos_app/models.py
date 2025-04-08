from django.db import models
from decimal import Decimal
from datetime import date
import logging


logger = logging.getLogger(__name__)

# Create your models here.
class Insumos(models.Model):
    UNIDADES_CHOICES = [
        ('g', 'Gramos'),
        ('kg', 'Kilogramos'),
        ('litros', 'Litros'),
        ('bultos', 'Bultos'),
    ]

    nombre_insumo = models.CharField(max_length=200)
    unidad_medida = models.CharField(max_length= 10, choices=UNIDADES_CHOICES)
    cantidad_disponible = models.IntegerField(default=0)

    def _str_(self):
        return f"{self.id}-{self.nombre_insumo}-{self.unidad_medida}-{self.cantidad_disponible}"
