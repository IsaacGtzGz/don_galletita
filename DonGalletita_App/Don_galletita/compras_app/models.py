from django.db import models
from proveedores_app.models import Proveedor
from insumos_app.models import Insumos

class Compra(models.Model):
    compra_id = models.AutoField(primary_key=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, db_column='proveedor_id')
    fecha_compra = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compra'

    def __str__(self):
        return f"Compra {self.compra_id} - Proveedor {self.proveedor.nombre}"


class DetalleCompra(models.Model):
    detalle_id = models.AutoField(primary_key=True)
    compra = models.ForeignKey(Compra, related_name='detalles', on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumos, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=10, choices=Insumos.UNIDADES_CHOICES)
    fecha_caducidad = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'detalle_compra'