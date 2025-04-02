from django.core.management.base import BaseCommand
from cliente_app.models import Cliente
from insumos_app.models import Insumos as Insumo
from ventas_app.models import Venta, DetalleVenta

class Command(BaseCommand):
    help = 'Carga datos iniciales para pruebas'

    def handle(self, *args, **kwargs):
        # Crear clientes
        cliente, _ = Cliente.objects.get_or_create(nombre="Juan Pérez", telefono="1234567890")

        # Crear insumos
        insumo, _ = Insumo.objects.get_or_create(nombre_insumo="Harina", cantidad_disponible=100, unidad_medida="kg")

        # Crear una venta
        venta, _ = Venta.objects.get_or_create(persona=cliente, estatus_venta="Pagado")

        # Crear un detalle de venta
        DetalleVenta.objects.get_or_create(venta=venta, producto=insumo, cantidad=5, precio_unitario=20, unidad_medida="kg")

        self.stdout.write(self.style.SUCCESS('Datos iniciales cargados correctamente.'))