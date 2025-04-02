from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.views.generic import FormView, DeleteView
from django.urls import reverse_lazy
from .models import Venta, DetalleVenta
from .forms import VentaForm, DetalleVentaForm
from reportlab.pdfgen import canvas
import base64
from io import BytesIO
from django.http import FileResponse

# Listar ventas
class ListaVentasView(TemplateView):
    template_name = 'lista_ventas.html'

    def get_context_data(self, **kwargs):
        lista = Venta.objects.all()
        return {'lista': lista}
    
# Crear una venta
class CrearVentaView(FormView):
    template_name = 'registrar_venta.html'  
    form_class = VentaForm
    success_url = reverse_lazy('lista_ventas')

    def form_valid(self, form):
        self.object = form.save()  # Asigna el objeto creado a self.object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('detalle_venta', kwargs={'venta_id': self.object.id})
    
# Editar una venta    
class EditarVentaView(FormView):
    template_name = 'editar_venta.html'  
    form_class = VentaForm
    success_url = reverse_lazy('lista_ventas')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        id = self.kwargs.get('id')
        venta = get_object_or_404(Venta, id=id)
        kwargs['instance'] = venta
        return kwargs
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

# Eliminar una venta
class EliminarVentaView(DeleteView):
    model = Venta
    template_name = 'confirmar_eliminar_venta.html'
    success_url = reverse_lazy('lista_ventas')

    def get_object(self, queryset=None):
        id = self.kwargs.get('id')
        return get_object_or_404(Venta, id=id)


# Agregar detalle de venta
class CrearDetalleVentaView(FormView):
    template_name = 'crear_detalle_venta.html'
    form_class = DetalleVentaForm

    def form_valid(self, form):
        venta_id = self.kwargs.get('venta_id')
        venta = get_object_or_404(Venta, id=venta_id)
        detalle_venta = form.save(commit=False)
        detalle_venta.venta = venta
        detalle_venta.save()
        return redirect('detalle_venta', venta_id=venta.id)

# Editar detalle de venta
class EditarDetalleVentaView(FormView):
    template_name = 'editar_detalle_venta.html'  
    form_class = DetalleVentaForm
    success_url = reverse_lazy('lista_ventas')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        id = self.kwargs.get('id')
        detalle_venta = get_object_or_404(DetalleVenta, id=id)
        kwargs['instance'] = detalle_venta
        return kwargs
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

# Eliminar un detalle de venta
class EliminarDetalleVentaView(DeleteView):
    model = DetalleVenta
    template_name = 'confirmar_eliminar_detalle.html'
    success_url = reverse_lazy('lista_ventas')

    def get_object(self, queryset=None):
        id = self.kwargs.get('id')
        return get_object_or_404(DetalleVenta, id=id)

    def get_success_url(self):
        detalle_venta = self.get_object()
        return reverse_lazy('detalle_venta', kwargs={'venta_id': detalle_venta.venta.id})

# Corte de ventas diario
class CorteVentasDiarioView(TemplateView):
    template_name = 'corte_ventas_diario.html'

    def get_context_data(self, **kwargs):
        from django.utils.timezone import now, timedelta
        hoy = now().date()
        ventas_diarias = Venta.objects.filter(fecha_venta__date=hoy)
        ventas_con_totales = []
        productos_vendidos = {}
        metodos_pago = {'efectivo': 0, 'tarjeta': 0, 'transferencia': 0}
        totales_por_categoria = {'piezas': 0, 'gramos': 0, 'kg': 0, 'gr700': 0}

        for venta in ventas_diarias:
            total_venta = 0
            for detalle in venta.detalles.all():
                total_venta += detalle.cantidad * detalle.precio_unitario

                # Contabilizar productos vendidos por categoría
                if detalle.unidad_medida == 'pieza':
                    totales_por_categoria['piezas'] += detalle.cantidad
                elif detalle.unidad_medida == 'gramos':
                    totales_por_categoria['gramos'] += detalle.cantidad
                elif detalle.unidad_medida == '1kg':
                    totales_por_categoria['kg'] += detalle.cantidad
                elif detalle.unidad_medida == '700gr':
                    totales_por_categoria['gr700'] += detalle.cantidad

                # Contabilizar productos vendidos
                if detalle.producto.nombre_insumo not in productos_vendidos:
                    productos_vendidos[detalle.producto.nombre_insumo] = 0
                productos_vendidos[detalle.producto.nombre_insumo] += detalle.cantidad

            # Contabilizar métodos de pago
            if venta.metodo_pago in metodos_pago:
                metodos_pago[venta.metodo_pago] += total_venta

            ventas_con_totales.append({'venta': venta, 'total': total_venta})

        total_ventas = sum(venta['total'] for venta in ventas_con_totales)
        total_transacciones = ventas_diarias.count()

        # Comparativa con días anteriores (últimos 7 días)
        comparativa_dias = []
        for i in range(1, 8):
            dia_anterior = hoy - timedelta(days=i)
            ventas_dia_anterior = Venta.objects.filter(fecha_venta__date=dia_anterior)
            total_dia_anterior = sum(
                detalle.cantidad * detalle.precio_unitario
                for venta in ventas_dia_anterior
                for detalle in venta.detalles.all()
            )
            comparativa_dias.append({
                'fecha': dia_anterior,
                'total_ventas': total_dia_anterior,
                'transacciones': ventas_dia_anterior.count()
            })

        return {
            'ventas_diarias': ventas_con_totales,
            'total_ventas': total_ventas,
            'total_transacciones': total_transacciones,
            'productos_vendidos': productos_vendidos,
            'metodos_pago': metodos_pago,
            'totales_por_categoria': totales_por_categoria,
            'comparativa_dias': comparativa_dias
        }
        
# Clase para generar y descargar el ticket
class TicketVentaView(TemplateView):
    def generar_ticket(self, venta):
        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(100, 800, f"Ticket de Venta - ID: {venta.id}")
        c.drawString(100, 780, f"Cliente: {venta.persona}")
        c.drawString(100, 760, f"Fecha: {venta.fecha_venta}")
        c.drawString(100, 740, "Detalles:")

        y = 720
        for detalle in venta.detalles.all():
            c.drawString(100, y, f"Producto: {detalle.producto.nombre_insumo}, Cantidad: {detalle.cantidad} {detalle.unidad_medida}, Precio: {detalle.precio_unitario}")
            y -= 20

        c.save()
        buffer.seek(0)
        venta.ticket = base64.b64encode(buffer.read()).decode('utf-8')
        venta.save()

    def get(self, request, *args, **kwargs):
        venta_id = kwargs.get('venta_id')
        venta = get_object_or_404(Venta, id=venta_id)
        if not venta.ticket:
            self.generar_ticket(venta)

        response = FileResponse(BytesIO(base64.b64decode(venta.ticket)), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="ticket_{venta.id}.pdf"'
        return response

# Detalle de una venta
class DetalleVentaView(TemplateView):
    template_name = 'detalle_venta.html'

    def get_context_data(self, **kwargs):
        venta_id = self.kwargs.get('venta_id')
        venta = get_object_or_404(Venta, id=venta_id)
        detalles = venta.detalles.all()
        return {'venta': venta, 'detalles': detalles}
