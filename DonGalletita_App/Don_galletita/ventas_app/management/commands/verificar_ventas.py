from django.core.management.base import BaseCommand
from ventas_app.models import Venta
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Verificar ventas registradas para el día actual'

    def handle(self, *args, **kwargs):
        hoy = now().date()
        ventas = Venta.objects.all()
        self.stdout.write(self.style.SUCCESS(f"Ventas registradas en la base de datos:"))
        for venta in ventas:
            self.stdout.write(f"ID: {venta.id}, Fecha: {venta.fecha_venta}, Cliente: {venta.persona}")

        ventas_hoy = Venta.objects.filter(fecha_venta__date=hoy)
        self.stdout.write(self.style.SUCCESS(f"Ventas registradas hoy ({hoy}):"))
        if ventas_hoy.exists():
            for venta in ventas_hoy:
                self.stdout.write(f"ID: {venta.id}, Fecha: {venta.fecha_venta}, Cliente: {venta.persona}")
        else:
            self.stdout.write(self.style.WARNING("No hay ventas registradas para el día actual."))