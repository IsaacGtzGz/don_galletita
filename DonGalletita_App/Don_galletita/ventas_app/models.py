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
                # Reducir inventario
                for detalle in self.detalles.all():
                    producto = detalle.producto
                    cantidad_a_descontar = detalle.cantidad

                    # Convertir la cantidad a kilogramos si es necesario
                    if detalle.unidad_medida == 'g':
                        cantidad_a_descontar /= Decimal('1000')  # Convertir gramos a kilogramos
                    elif detalle.unidad_medida == 'pz':
                        cantidad_a_descontar *= producto.peso_unidad  # Usar el peso por unidad del producto

                    # Aplicar merma (2%)
                    cantidad_a_descontar += cantidad_a_descontar * Decimal('0.02')

                    if producto.cantidad_disponible >= cantidad_a_descontar:
                        producto.cantidad_disponible -= cantidad_a_descontar
                        producto.save()
                    else:
                        raise ValueError(f"Stock insuficiente para el producto {producto.nombre}.")

        super().save(*args, **kwargs)


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('productos_app.Producto', on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0)])
    unidad_medida = models.CharField(
        max_length=2,
        choices=[('kg', 'kg'), ('g', 'g'), ('pz', 'pz')]
    )
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])


