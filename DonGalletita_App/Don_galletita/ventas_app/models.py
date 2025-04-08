from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


class Venta(models.Model):
    persona = models.ForeignKey('cliente_app.Cliente', on_delete=models.CASCADE)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    estatus_venta = models.CharField(
        max_length=10,
        choices=[('Pagado', 'Pagado'), ('Pendiente', 'Pendiente'), ('Cancelado', 'Cancelado')],
        default='Pendiente'
    )
    ticket = models.TextField(null=True, blank=True)  # Cambiado de FileField a TextField para almacenar Base64
    metodo_pago = models.CharField(
        max_length=15,
        choices=[('efectivo', 'Efectivo')],  # Solo efectivo
        default='efectivo'
    )
    estado_entrega = models.CharField(
        max_length=15,
        choices=[('entregado', 'Entregado'), ('pendiente', 'Pendiente'), ('cancelado', 'Cancelado')],
        default='pendiente'
    )


    def __str__(self):
        return f"Venta {self.id} - {self.persona}"

    def save(self, *args, **kwargs):
        # Verificar si el estatus cambia a 'Pagado'
        if self.pk:  # Si la venta ya existe
            venta_anterior = Venta.objects.get(pk=self.pk)
            if venta_anterior.estatus_venta != 'Pagado' and self.estatus_venta == 'Pagado':
                # Reducir inventario solo cuando el estatus cambie a 'Pagado'
                for detalle in self.detalles.all():
                    producto = detalle.producto
                    cantidad_a_descontar = detalle.cantidad

                    # Ajustar el cálculo según la unidad de medida
                    if detalle.unidad_medida == 'g':
                        piezas_necesarias = cantidad_a_descontar / producto.peso_unidad
                    elif detalle.unidad_medida == '1kg':
                        piezas_necesarias = (cantidad_a_descontar * 1000) / producto.peso_unidad
                    elif detalle.unidad_medida == '700gr':
                        piezas_necesarias = (cantidad_a_descontar * 700) / producto.peso_unidad
                    elif detalle.unidad_medida == 'pz':
                        piezas_necesarias = cantidad_a_descontar  # Ya está en piezas

                    if producto.cantidad_disponible >= piezas_necesarias:
                        producto.cantidad_disponible -= piezas_necesarias
                        producto.save()
                    else:
                        raise ValueError(f"Stock insuficiente para el producto {producto.nombre}.")

        super().save(*args, **kwargs)


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('productos_app.Producto', on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0)])
    unidad_medida = models.CharField(
        max_length=6,  # Ajustado para soportar '700gr'
        choices=[('kg', 'kg'), ('g', 'g'), ('pz', 'pz'), ('1kg', '1kg'), ('700gr', '700gr')]
    )
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])


