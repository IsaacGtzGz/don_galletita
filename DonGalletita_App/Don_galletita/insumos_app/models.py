from django.db import models
from decimal import Decimal
import logging


logger = logging.getLogger(__name__)

# Create your models here.
class Insumos(models.Model):
    UNIDADES_CHOICES = [
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
        ('pz', 'Piezas'),
    ]

    nombre_insumo = models.CharField(max_length=200)
    unidad_medida = models.CharField(max_length= 10, choices=UNIDADES_CHOICES)
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=3)
    fecha_caducidad = models.DateField(null=True, blank=True)

    def convertir_unidad(self, nueva_unidad):
        print(f"Convertir de {self.unidad_medida} a {nueva_unidad}")
        if self.unidad_medida == 'kg' and nueva_unidad == 'g':
            self.cantidad_disponible * 1000
        elif self.unidad_medida == 'g' and nueva_unidad == 'kg':
            self.cantidad_disponible / 1000
        elif self.unidad_medida == 'l' and nueva_unidad == 'ml':
            self.cantidad_disponible * 1000
        elif self.unidad_medida == 'ml' and nueva_unidad == 'l':
            self.cantidad_disponible / 1000
        self.unidad_medida = nueva_unidad
        print(f"Cantidad convertida: {self.cantidad_disponible} {self.unidad_medida}")

    def save(self, *args, **kwargs):
        print(f"Guardando insumo con cantidad: {self.cantidad_disponible} y unidad: {self.unidad_medida}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}-{self.nombre_insumo}-{self.unidad_medida}-{self.cantidad_disponible}"
