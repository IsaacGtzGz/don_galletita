from django.db import models
from decimal import Decimal

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
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fecha_caducidad = models.DateField(null=True, blank=True)

     
    def convertir_unidades(self, nueva_unidad):
        """ Convierte la cantidad disponible a otra unidad si es compatible """
        conversiones = {
            ('kg', 'g'): Decimal('1000'),
            ('g', 'kg'): Decimal('0.001'),
            ('l', 'ml'): Decimal('1000'),
            ('ml', 'l'): Decimal('0.001'),
        }

        print(f"Unidad actual: {self.unidad_medida}, Nueva unidad: {nueva_unidad}")

        # Evita conversión si la unidad es la misma
        if self.unidad_medida == nueva_unidad:
            print("La unidad es la misma, no se hace conversión.")
            return

        # Verifica si la conversión es válida
        factor_conversion = conversiones.get((self.unidad_medida, nueva_unidad))

        if factor_conversion is None:
            print(f"⚠️ No se encontró conversión válida de {self.unidad_medida} a {nueva_unidad}")
            return

        # Aplica la conversión y actualiza la unidad
        self.cantidad_disponible *= factor_conversion
        self.unidad_medida = nueva_unidad

        print(f"Cantidad después de conversión: {self.cantidad_disponible} {self.unidad_medida}")

        self.save()

    def __str__(self):
        return f"{self.id}-{self.nombre_insumo}-{self.unidad_medida}-{self.cantidad_disponible}"
