from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from usuarios_app.models import Usuario

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
    
class Producto(models.Model):
    UNIDADES_MEDIDA = (
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('pz', 'Piezas')
    )
    
    producto_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=2, choices=UNIDADES_MEDIDA)
    cantidad_disponible = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    peso_unidad = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_caducidad = models.DateField()
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    class Meta:
        db_table = 'producto'

class Venta(models.Model):
    ESTADOS = (
        ('Pagado', 'Pagado'),
        ('Pendiente', 'Pendiente'),
        ('Cancelado', 'Cancelado')
    )
    
    venta_id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    estatus_venta = models.CharField(max_length=10, choices=ESTADOS, default='Pendiente')
    
    class Meta:
        db_table = 'venta'
    
    def calcular_total(self):
        return sum(d.subtotal for d in self.detalleventa_set.all())

class DetalleVenta(models.Model):
    UNIDADES_MEDIDA = (
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('pz', 'Piezas')
    )
    
    detalle_venta_id = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    unidad_medida = models.CharField(max_length=2, choices=UNIDADES_MEDIDA)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'detalle_venta'
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario