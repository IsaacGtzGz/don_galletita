from django.db import models


class Venta(models.Model):
    persona = models.ForeignKey('cliente_app.Cliente', on_delete=models.CASCADE)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    estatus_venta = models.CharField(
        max_length=10,
        choices=[('Pagado', 'Pagado'), ('Pendiente', 'Pendiente'), ('Cancelado', 'Cancelado'), ('Reservado', 'Reservado')],
        default='Pendiente'
    )
    ticket = models.TextField(null=True, blank=True)  # Cambiado de FileField a TextField para almacenar Base64
    metodo_pago = models.CharField(
        max_length=15,
        choices=[('efectivo', 'Efectivo')],  # Solo efectivo
        default='efectivo'
    )

    def __str__(self):
        return f"Venta {self.id} - {self.persona}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('insumos_app.Insumos', on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    unidad_medida = models.CharField(
        max_length=2,
        choices=[('kg', 'kg'), ('g', 'g'), ('pz', 'pz')]
    )
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)


