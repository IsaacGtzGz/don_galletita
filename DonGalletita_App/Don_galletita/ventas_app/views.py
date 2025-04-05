from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.base import TemplateView
from django.views.generic import FormView, DeleteView
from django.urls import reverse_lazy
from .models import Venta, DetalleVenta
from .forms import VentaForm, DetalleVentaForm
from reportlab.pdfgen import canvas
from django.http import FileResponse, JsonResponse, HttpResponse
from io import BytesIO
import base64
from reportlab.lib.pagesizes import inch, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from django.db.models.functions import TruncDate
from django.utils.timezone import now, localtime, timezone
from datetime import timedelta
import io
import openpyxl
from openpyxl.styles import Font
from django.db import transaction
from django.db.models import Sum, Count
from productos_app.models import Producto
import json
import requests
from math import floor
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.base import TemplateView
from django.views.generic import FormView, DeleteView
from django.urls import reverse_lazy
from .models import Venta, DetalleVenta
from .forms import VentaForm, DetalleVentaForm
from reportlab.pdfgen import canvas
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from io import BytesIO
import base64
from reportlab.lib.pagesizes import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import base64
from io import BytesIO
from django.http import FileResponse
from django.db.models.functions import TruncDate
from django.utils.timezone import now, localtime
from datetime import timedelta
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
import io
import openpyxl
from openpyxl.styles import Font
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Count
from ventas_app.models import DetalleVenta
from productos_app.models import Producto
from datetime import timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import json
    
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Sum, Count
from ventas_app.models import DetalleVenta, Venta
from productos_app.models import Producto
from datetime import timedelta


def obtener_detalle_producto(request, producto_id, unidad_medida, cantidad):
    try:
        producto = Producto.objects.get(producto_id=producto_id)  # Corregido para usar producto_id
        cantidades_disponibles = []

        # Ajustar el cálculo de cantidades disponibles para evitar opciones inválidas
        if unidad_medida == 'g':
            max_gramos = producto.cantidad_disponible * producto.peso_unidad
            cantidades_disponibles = [i for i in range(int(producto.peso_unidad), int(max_gramos) + 1, int(producto.peso_unidad)) if i <= max_gramos]
        elif unidad_medida == '1kg':
            max_kilos = floor((producto.cantidad_disponible * producto.peso_unidad) / 1000)
            cantidades_disponibles = [i for i in range(1, max_kilos + 1)]
        elif unidad_medida == '700gr':
            max_paquetes = floor((producto.cantidad_disponible * producto.peso_unidad) / 700)
            cantidades_disponibles = [i for i in range(1, max_paquetes + 1)]
        else:  # 'pz'
            cantidades_disponibles = [i for i in range(1, int(producto.cantidad_disponible) + 1)]

        detalle = {
            'cantidades_disponibles': cantidades_disponibles,
            'peso_unidad': producto.peso_unidad,
            'cantidad_disponible': producto.cantidad_disponible
        }
        return JsonResponse({'detalle': detalle})
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado.'}, status=404)

# Listar ventas
class ListaVentasView(TemplateView):
    template_name = 'lista_ventas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lista_pagadas = Venta.objects.filter(estatus_venta='Pagado').order_by('-id')
        lista_pendientes = Venta.objects.filter(estatus_venta='Pendiente').order_by('-id')
        lista_canceladas = Venta.objects.filter(estatus_venta='Cancelado').order_by('-id')
        context['lista_pagadas'] = lista_pagadas
        context['lista_pendientes'] = lista_pendientes
        context['lista_canceladas'] = lista_canceladas
        return context
    
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

        # Calcular cuántas piezas se necesitan según la unidad de medida
        producto = detalle_venta.producto
        if detalle_venta.unidad_medida == 'g':
            piezas_necesarias = detalle_venta.cantidad / producto.peso_unidad
        elif detalle_venta.unidad_medida == '1kg':
            piezas_necesarias = (1000 / producto.peso_unidad) * detalle_venta.cantidad
        elif detalle_venta.unidad_medida == '700gr':
            piezas_necesarias = (700 / producto.peso_unidad) * detalle_venta.cantidad
        else:
            piezas_necesarias = detalle_venta.cantidad

        # Validar inventario
        if producto.cantidad_disponible < piezas_necesarias:
            form.add_error('cantidad', 'No hay suficiente inventario para esta venta.')
            return self.form_invalid(form)

        # Descontar del inventario
        producto.cantidad_disponible -= piezas_necesarias
        producto.save()

        # Asignar el precio unitario del producto al detalle de la venta
        detalle_venta.precio_unitario = producto.precio_unitario

        # Crear el detalle de la venta
        detalle_venta.save()

        # Incluir el token CSRF en la petición a producción
        csrf_token = self.request.META.get('CSRF_COOKIE', '')
        headers = {'X-CSRFToken': csrf_token}
        if producto.cantidad_disponible < 80:
            cantidad_a_producir = 150 - producto.cantidad_disponible
            response = requests.post(
                'http://127.0.0.1:8000/produccion/crear/',
                data={
                    'producto_id': producto.producto_id,
                    'cantidad_necesaria': cantidad_a_producir
                },
                headers=headers
            )
            if response.status_code != 200:
                form.add_error(None, 'No se pudo realizar la producción por falta de stock o error en el servidor.')
                return self.form_invalid(form)

        # Verificar si se necesita producción automática
        if producto.cantidad_disponible < 80:
            cantidad_a_producir = 150 - producto.cantidad_disponible
            try:
                from produccion_app.views import crear_produccion_automatica
                crear_produccion_automatica(producto.producto_id, cantidad_a_producir)
            except ValueError as e:
                form.add_error(None, f"Error al crear producción automática: {str(e)}")
                return self.form_invalid(form)

        return redirect('detalle_venta', venta_id=venta.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venta_id'] = self.kwargs.get('venta_id')
        return context

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
        from django.utils.timezone import now, localdate
        from django.db.models import Sum
        hoy = localdate()

        # Filtrar ventas del día actual
        hoy_inicio = localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        hoy_fin = localtime().replace(hour=23, minute=59, second=59, microsecond=999999)
        ventas_diarias = Venta.objects.filter(fecha_venta__range=(hoy_inicio, hoy_fin)).order_by('-id')

        # Filtrar solo ventas pagadas para el total del día
        # Calcular el total de ventas solo para ventas pagadas
        total_ventas = sum(
            sum(detalle.cantidad * detalle.precio_unitario for detalle in venta.detalles.all())
            for venta in ventas_diarias.filter(estatus_venta='Pagado')
        )
        total_ventas = round(total_ventas, 2)

        total_transacciones = ventas_diarias.count()

        # Totales por tipo de presentación
        totales_por_categoria = {
            'piezas': 0,
            'gramos': 0,
            'kg': 0,
            'gr700': 0
        }
        productos_vendidos = {}

        for venta in ventas_diarias:
            for detalle in venta.detalles.all():
                if detalle.unidad_medida == 'pz':
                    totales_por_categoria['piezas'] += detalle.cantidad
                elif detalle.unidad_medida == 'g':
                    totales_por_categoria['gramos'] += detalle.cantidad
                elif detalle.unidad_medida == 'kg':
                    totales_por_categoria['kg'] += detalle.cantidad
                elif detalle.unidad_medida == '700gr':
                    totales_por_categoria['gr700'] += detalle.cantidad

        # Comparativa con el día anterior
        dia_anterior = hoy - timedelta(days=1)
        ventas_dia_anterior = Venta.objects.filter(fecha_venta__date=dia_anterior).order_by('-id')
        total_dia_anterior = ventas_dia_anterior.aggregate(total=Sum('detalles__precio_unitario'))['total'] or 0

        ventas_con_totales = []
        for venta in ventas_diarias:
            total_venta = sum(
                detalle.cantidad * detalle.precio_unitario
                for detalle in venta.detalles.all()
            )
            ventas_con_totales.append({
                'id': venta.id,
                'cliente': venta.persona,
                'fecha': venta.fecha_venta,
                'total': total_venta
            })

        ventas_pagadas = []
        ventas_otros = []

        for venta in ventas_diarias:
            total_venta = sum(
                detalle.cantidad * detalle.precio_unitario
                for detalle in venta.detalles.all()
            )
            venta_data = {
                'id': venta.id,
                'cliente': venta.persona,
                'fecha': venta.fecha_venta,
                'estatus': venta.estatus_venta,
                'total': total_venta
            }
            if venta.estatus_venta == 'Pagado':
                ventas_pagadas.append(venta_data)
            else:
                ventas_otros.append(venta_data)

        return {
            'ventas_diarias': ventas_con_totales,
            'ventas_pagadas': ventas_pagadas,
            'ventas_otros': ventas_otros,
            'total_ventas': total_ventas,
            'total_transacciones': total_transacciones,
            'totales_por_categoria': totales_por_categoria,
            'total_dia_anterior': total_dia_anterior
        }
        
    def post(self, request, *args, **kwargs):
        hoy = now().date()
        ventas_diarias = Venta.objects.filter(fecha_venta__date=hoy)

        # Validación: Bloquear cierre si hay ventas sin cliente asociado
        ventas_sin_cliente = ventas_diarias.filter(persona__isnull=True)
        if ventas_sin_cliente.exists():
            return self.render_to_response({
                'error': 'No se puede cerrar el día. Existen ventas sin cliente asociado.'
            })

        # Generar tickets para todas las ventas del día
        for venta in ventas_diarias:
            if not venta.ticket:
                TicketVentaView().generar_ticket(venta)

        # Validación: Alertar si hay discrepancias en el efectivo
        total_ventas = sum(
            detalle.cantidad * detalle.precio_unitario
            for venta in ventas_diarias
            for detalle in venta.detalles.all()
        )
        efectivo_fisico = float(request.POST.get('efectivo_fisico', 0))
        if efectivo_fisico != total_ventas:
            return self.render_to_response({
                'error': f'Discrepancia detectada. Total registrado: {total_ventas}, Efectivo físico: {efectivo_fisico}'
            })

        return self.render_to_response({
            'success': 'Corte diario completado exitosamente.'
        })

# Clase para generar y descargar el ticket
class TicketVentaView(TemplateView):
    def generar_ticket(self, venta):
        # Configuración del tamaño del ticket (más ancho para nombres largos)
        ticket_width = 4.0 * inch
        ticket_height = 8 * inch
        custom_size = (ticket_width, ticket_height)
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=custom_size, 
                               leftMargin=0.2*inch, rightMargin=0.2*inch,
                               topMargin=0.2*inch, bottomMargin=0.2*inch)

        styles = getSampleStyleSheet()

        # Estilos personalizados
        large_bold_style = ParagraphStyle(
            name='LargeBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            alignment=1,  # Centrado
            spaceAfter=12
        )
        bold_centered_style = ParagraphStyle(
            name='BoldCentered',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            alignment=1,
            spaceAfter=6
        )
        centered_style = ParagraphStyle(
            name='Centered',
            parent=styles['Normal'],
            alignment=1,
            spaceAfter=6,
            fontSize=10
        )
        product_style = ParagraphStyle(
            name='ProductStyle',
            parent=styles['Normal'],
            fontSize=8,
            alignment=0,  # Alineado a la izquierda
            leading=9,    # Espacio entre líneas
            wordWrap='LTR'
        )
        elements = []

        # Encabezado del Ticket
        elements.append(Paragraph("DON GALLETITA", large_bold_style))
        elements.append(Spacer(1, 12))
        # Información de la tienda (personaliza con tus datos)
        elements.append(Paragraph("Universidad Tecnologica de Leon", centered_style))
        elements.append(Paragraph("San Carlos, la roncha", centered_style))
        elements.append(Paragraph("Leon Guanajuato", centered_style))
        elements.append(Spacer(1, 12))
        # Información del cliente/venta
        elements.append(Paragraph(f"Cliente: {venta.persona}", centered_style))
        elements.append(Paragraph(f"Ticket: {venta.id}", centered_style))
        elements.append(Spacer(1, 12))

        # Línea de separación
        elements.append(Paragraph("--------------------------------", centered_style))

        # Tabla de productos
        data = [["Producto", "Cantidad", "Unidad", "Precio", "Total"]]
        total = 0

        for detalle in venta.detalles.all():
            # Calcular el subtotal ajustando el precio según la unidad de medida
            if detalle.unidad_medida == 'g':  # Si la unidad es gramos
                subtotal = (detalle.precio_unitario / 1000) * detalle.cantidad
            elif detalle.unidad_medida == 'kg':  # Si la unidad es kilogramos
                subtotal = detalle.precio_unitario * detalle.cantidad
            else:  # Si es otra unidad, usar el precio unitario directamente
                subtotal = detalle.precio_unitario * detalle.cantidad

            total += subtotal

            # Usamos Paragraph para permitir múltiples líneas en nombres largos
            product_name = Paragraph(detalle.producto.nombre, product_style)

            data.append([
                product_name,
                Paragraph(f"{detalle.cantidad}", centered_style),
                Paragraph(f"{detalle.unidad_medida}", centered_style),
                Paragraph(f"${detalle.precio_unitario:.2f}", centered_style),
                Paragraph(f"${subtotal:.2f}", centered_style)
            ])

        col_widths = [
            ticket_width*0.25,  # Producto
            ticket_width*0.15,  # Cantidad
            ticket_width*0.15,  # Unidad
            ticket_width*0.20,  # Precio
            ticket_width*0.25   # Total
        ]

        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Estilo para la fila de encabezados
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.8, 0.8, 0.8)),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            # Estilo para el contenido
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('LEADING', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 6))

        # Total
        elements.append(Paragraph(f"<b>Total:</b> ${total:.2f}", centered_style))
        elements.append(Paragraph("--------------------------------", centered_style))

        # Información de la transacción
        elements.append(Paragraph(f"Fecha: {venta.fecha_venta.strftime('%d/%m/%Y %H:%M')}", centered_style))
        elements.append(Spacer(1, 12))

        # Mensajes finales
        elements.append(Paragraph("¡Gracias por su compra!", centered_style))
        elements.append(Paragraph("Por favor vuelva pronto", centered_style))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Don Galletita", centered_style))
        pdf.build(elements)
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

        # Calcular el subtotal ajustando el precio según la unidad de medida
        detalles_con_subtotal = []
        for detalle in detalles:
            if detalle.unidad_medida == 'g':  # Si la unidad es gramos
                precio_proporcional = (detalle.precio_unitario / 1000) * detalle.cantidad
            elif detalle.unidad_medida == 'kg':  # Si la unidad es kilogramos
                precio_proporcional = detalle.precio_unitario * detalle.cantidad
            else:  # Si es otra unidad, usar el precio unitario directamente
                precio_proporcional = detalle.precio_unitario * detalle.cantidad

            detalles_con_subtotal.append({
                'producto': detalle.producto,
                'cantidad': detalle.cantidad,
                'unidad_medida': detalle.unidad_medida,
                'precio_unitario': detalle.precio_unitario,
                'subtotal': precio_proporcional,
                'id': detalle.id
            })

        # Calcular el total a pagar
        total_a_pagar = sum(detalle['subtotal'] for detalle in detalles_con_subtotal)

        return {
            'venta': venta,
            'detalles': detalles_con_subtotal,
            'total_a_pagar': total_a_pagar
        }
# Exportar reporte en PDF
class ExportarReportePDFView(TemplateView):
    def get(self, request, *args, **kwargs):
        from django.utils.timezone import localtime
        from django.db.models import Sum
        hoy_inicio = localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        hoy_fin = localtime().replace(hour=23, minute=59, second=59, microsecond=999999)
        ventas_diarias = Venta.objects.filter(fecha_venta__range=(hoy_inicio, hoy_fin)).order_by('-id')

        total_ventas = ventas_diarias.aggregate(total=Sum('detalles__precio_unitario'))['total'] or 0
        total_transacciones = ventas_diarias.count()

        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter,
                                 leftMargin=0.5 * inch, rightMargin=0.5 * inch,
                                 topMargin=0.5 * inch, bottomMargin=0.5 * inch)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name='Title',
            fontName='Helvetica-Bold',
            fontSize=16,
            alignment=1,  # Centrado
            spaceAfter=12
        )
        subtitle_style = ParagraphStyle(
            name='Subtitle',
            fontName='Helvetica',
            fontSize=12,
            alignment=1,
            spaceAfter=6
        )
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])

        elements = []
        elements.append(Paragraph("DON GALLETITA", title_style))
        elements.append(Paragraph("Universidad Tecnológica de León", subtitle_style))
        elements.append(Paragraph("San Carlos, La Roncha, León, Guanajuato", subtitle_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Reporte Diario de Ventas - Fecha: {localtime().strftime('%d/%m/%Y')}", subtitle_style))
        elements.append(Spacer(1, 12))
        
        # Tabla de Ventas Pagadas
        elements.append(Paragraph("Ventas Pagadas", title_style))
        elements.append(Spacer(1, 12))
        data_pagadas = [["ID", "Cliente", "Fecha", "Total"]]
        for venta in ventas_diarias.filter(estatus_venta='Pagado'):
            total_venta = sum(
                detalle.cantidad * detalle.precio_unitario
                for detalle in venta.detalles.all()
            )
            data_pagadas.append([venta.id, str(venta.persona), str(venta.fecha_venta), f"${total_venta:.2f}"])

        table_pagadas = Table(data_pagadas, colWidths=[1.5 * inch, 2.5 * inch, 2.5 * inch, 1.5 * inch])
        table_pagadas.setStyle(table_style)
        elements.append(table_pagadas)
        elements.append(Spacer(1, 12))

        # Tabla de Ventas Pendientes y Canceladas
        elements.append(Paragraph("Ventas Pendientes y Canceladas", title_style))
        elements.append(Spacer(1, 12))
        data_otros = [["ID", "Cliente", "Fecha", "Estatus", "Total"]]
        for venta in ventas_diarias.exclude(estatus_venta='Pagado'):
            total_venta = sum(
                detalle.cantidad * detalle.precio_unitario
                for detalle in venta.detalles.all()
            )
            data_otros.append([venta.id, str(venta.persona), str(venta.fecha_venta), venta.estatus_venta, f"${total_venta:.2f}"])

        table_otros = Table(data_otros, colWidths=[1.5 * inch, 2.5 * inch, 2.5 * inch, 1.5 * inch, 1.5 * inch])
        table_otros.setStyle(table_style)
        elements.append(table_otros)

        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Total Ventas: ${total_ventas:.2f}", subtitle_style))
        elements.append(Paragraph(f"Total Transacciones: {total_transacciones}", subtitle_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("¡Mejorando la calidad de nuestros productos!", subtitle_style))

        pdf.build(elements)
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_diario.pdf"'
        return response

# Exportar reporte en Excel
class ExportarReporteExcelView(TemplateView):
    def get(self, request, *args, **kwargs):
        from django.utils.timezone import localtime
        from django.db.models import Sum
        hoy_inicio = localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        hoy_fin = localtime().replace(hour=23, minute=59, second=59, microsecond=999999)
        ventas_diarias = Venta.objects.filter(fecha_venta__range=(hoy_inicio, hoy_fin)).order_by('-id')

        # Crear un libro de Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Reporte Diario"

        # Título del reporte
        ws.merge_cells("A1:D1")
        ws["A1"] = "Reporte Diario de Ventas"
        ws["A1"].font = Font(bold=True, size=14)

        # Encabezados
        headers = ["ID", "Cliente", "Fecha", "Total"]
        ws.append(headers)

        # Datos del reporte
        for venta in ventas_diarias:
            total_venta = sum(
                detalle.cantidad * detalle.precio_unitario
                for detalle in venta.detalles.all()
            )
            ws.append([venta.id, str(venta.persona), str(venta.fecha_venta), total_venta])

        # Guardar el archivo en memoria
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="reporte_diario.xlsx"'
        wb.save(response)
        return response

# Confirmar venta
class ConfirmarVentaView(TemplateView):
    def post(self, request, *args, **kwargs):
        venta_id = kwargs.get('venta_id')
        venta = get_object_or_404(Venta, id=venta_id)

        # Descuento automático de existencias
        with transaction.atomic():
            for detalle in venta.detalles.all():
                producto = detalle.producto
                cantidad_a_descontar = detalle.cantidad

                # Aplicar merma (2%)
                cantidad_a_descontar += cantidad_a_descontar * 0.02

                if producto.cantidad_disponible >= cantidad_a_descontar:
                    producto.cantidad_disponible -= cantidad_a_descontar
                    producto.save()
                else:
                    return self.render_to_response({
                        'error': f"Stock insuficiente para el producto {producto.nombre}."
                    })

        # Actualizar estatus de la venta
        venta.estatus_venta = 'Entregado'
        venta.save()

        return redirect('detalle_venta', venta_id=venta.id)
    

 # Dashboard de presentaciones y alertas

#Dashboard de presentaciones y alertas
class DashboardPresentacionesAlertasView(TemplateView):
    template_name = 'dashboard_presentaciones_alertas.html'
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
         
        # --- Gráfico de Presentaciones Más Vendidas ---
        ventas_30_dias = Venta.objects.filter(
            fecha_venta__gte=timezone.now() - timedelta(days=30)
        ).order_by('-id')
         
        detalles = DetalleVenta.objects.filter(venta__in=ventas_30_dias)
         
        # Agrupar por tipo de presentación
        presentaciones_data = detalles.values('unidad_medida').annotate(
            total_vendido=Sum('cantidad'),
            total_ventas=Count('id')
        ).order_by('-total_vendido')
         
        # Preparar datos para el gráfico con nombres y colores para galletas
        context['presentaciones_chart'] = {
            'labels': json.dumps([self.get_presentation_name(p['unidad_medida']) for p in presentaciones_data]),
            'data': json.dumps([float(p['total_vendido']) for p in presentaciones_data]),
            'colors': json.dumps(['#F4A261', '#2A9D8F', '#E9C46A', '#E76F51', '#264653'])
        }
         
        # --- Alertas de Caducidad ---
        fecha_limite = timezone.now().date() + timedelta(days=2)
        context['productos_proximos_caducar'] = Producto.objects.filter(
            fecha_caducidad__lte=fecha_limite,
            fecha_caducidad__gte=timezone.now().date(),
            cantidad_disponible__gt=0
        ).order_by('fecha_caducidad')
        
        # Desglose por tipo de presentación
        desglose_presentaciones = detalles.values('unidad_medida').annotate(
            total_vendido=Sum('cantidad')
        ).order_by('-total_vendido')

        context['desglose_presentaciones'] = desglose_presentaciones
         
        return context
     
    def get_presentation_name(self, unidad_medida):
        # Mapeo de códigos a nombres legibles para galletas
        presentation_names = {
            'kg': 'Bolsas 1kg',
            'g': 'Granel (100g)',
            'pz': 'Cajas Individuales',
            '1kg': 'Paquetes Familiares',
            '700g': 'Promo Especial'
        }
        return presentation_names.get(unidad_medida, unidad_medida)

# Dashboard de métricas de ventas
class DashboardMetricasVentasView(TemplateView):
    template_name = 'dashboard_metricas_ventas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoy_inicio = localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        hoy_fin = localtime().replace(hour=23, minute=59, second=59, microsecond=999999)

        # Ventas del día actual
        ventas_hoy = Venta.objects.filter(fecha_venta__range=(hoy_inicio, hoy_fin)).order_by('-id')
        total_ventas_hoy = ventas_hoy.aggregate(total=Sum('detalles__precio_unitario'))['total'] or 0
        total_transacciones = ventas_hoy.count()
        ticket_promedio = float(total_ventas_hoy) / total_transacciones if total_transacciones > 0 else 0

        # Productos más vendidos
        productos_vendidos = DetalleVenta.objects.filter(venta__in=ventas_hoy).values(
            'producto__nombre'
        ).annotate(
            cantidad_vendida=Sum('cantidad')
        ).order_by('-cantidad_vendida')

        # Preparar datos para el gráfico de productos más vendidos
        productos_labels = [producto['producto__nombre'] for producto in productos_vendidos]
        productos_data = [float(producto['cantidad_vendida']) for producto in productos_vendidos]

        # Preparar datos para el gráfico de progreso de ventas por hora
        ventas_por_hora = ventas_hoy.annotate(hora=TruncDate('fecha_venta')).values('hora').annotate(
            total=Sum('detalles__precio_unitario')
        ).order_by('hora')

        # Validar que 'hora' no sea None antes de formatear
        horas = [venta['hora'].strftime('%H:%M') if venta['hora'] else 'Sin datos' for venta in ventas_por_hora]
        montos = [float(venta['total']) for venta in ventas_por_hora]

        context.update({
            'total_ventas_hoy': float(total_ventas_hoy),
            'total_transacciones': total_transacciones,
            'ticket_promedio': ticket_promedio,
            'productos_vendidos': productos_vendidos,
            'productos_labels': json.dumps(productos_labels),
            'productos_data': json.dumps(productos_data),
            'horas': json.dumps(horas),
            'montos': json.dumps(montos),
        })
        return context