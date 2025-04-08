from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from usuarios_app.models import Usuario
from productos_app.models import Producto
from ventas_app.models import Venta, DetalleVenta

# Create your models here.
class Cliente(models.Model):
    cliente_id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE,
        related_name='cliente'
    )
    nombre = models.CharField(max_length=255)
    apellido_paterno = models.CharField(max_length=255)
    apellido_materno = models.CharField(max_length=255)
    telefono = models.CharField(max_length=10)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"
    
    class Meta:
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['cliente_id']
    
    ventas = models.ManyToManyField(
        'ventas_app.Venta',
        blank=True,
        related_name='clientes'
    )

class Carrito(models.Model):
    cliente = models.ForeignKey('cliente_app.Cliente', on_delete=models.CASCADE)
    producto = models.ForeignKey('productos_app.Producto', on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    unidad_medida = models.CharField(
        max_length=2,
        choices=[('kg', 'kg'), ('g', 'g'), ('pz', 'pz')]
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.cliente.nombre} con {self.cantidad} de {self.producto.nombre}"
