from django.db import models
from decimal import Decimal
from datetime import date

# Create your models here.
class Insumos(models.Model):
    UNIDADES_CHOICES = [
        ('g', 'Gramos'),
        ('kg', 'Kilogramos'),
        ('litros', 'Litros'),
        ('bultos', 'Bultos'),
    ]

    nombre_insumo = models.CharField(max_length=200)
    unidad_medida = models.CharField(max_length=10, choices=UNIDADES_CHOICES, default='g')
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fecha_caducidad = models.DateField(null=True, blank=True)
    conversion_bulto = models.DecimalField(max_digits=10, decimal_places=3, default=50000)  # Ejemplo: 1 bulto = 50,000g
    estado = models.CharField(max_length=20, default='activo')  # Nuevo campo para estado

    def convertir_unidades(self, unidad_destino):
        if self.unidad_medida == 'kg' and unidad_destino == 'g':
            return self.cantidad_disponible * 1000
        elif self.unidad_medida == 'litros' and unidad_destino == 'g':
            return self.cantidad_disponible * 1000  # Ajusta según el insumo
        elif self.unidad_medida == 'bultos' and unidad_destino == 'g':
            return self.cantidad_disponible * self.conversion_bulto
        return self.cantidad_disponible

    def verificar_caducidad(self):
        if self.fecha_caducidad and self.fecha_caducidad < date.today():
            self.estado = 'merma'  # Cambiar estado a "merma"
            self.save()

    def __str__(self):
        return f"{self.id}-{self.nombre_insumo}-{self.unidad_medida}-{self.cantidad_disponible}"
