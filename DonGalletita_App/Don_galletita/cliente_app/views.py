from django.shortcuts import render,reverse, redirect, get_object_or_404
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.units import inch
from django.utils import timezone
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.core.exceptions import ValidationError
from django.contrib.auth import login
from django.db.models import Q
from django.contrib import messages
from productos_app.models import Producto 
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from .models import Cliente, Producto, Venta, DetalleVenta
from .forms import RegistroClienteForm, CarritoForm, ClienteForm
from usuarios_app.models import Usuario
from django.core.exceptions import ObjectDoesNotExist
from .models import Venta, Producto, Carrito
from django.http import HttpResponse
from django.template.loader import get_template
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse


# Función para verificar roles permitidos
def lista_clientes(request):
    query = request.GET.get('q')
    if query:
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=query) |
            Q(apellido_paterno__icontains=query) |
            Q(apellido_materno__icontains=query) |
            Q(telefono__icontains=query) |
            Q(cliente_id__icontains=query)
        ).order_by('-fecha_registro')
    else:
        clientes = Cliente.objects.all().order_by('-fecha_registro')
    
    paginator = Paginator(clientes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'lista_clientes.html', {'page_obj': page_obj})

def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente {cliente.cliente_id} creado exitosamente.')
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'cliente_form.html', {'form': form})

def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, cliente_id=cliente_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cliente {cliente_id} actualizado exitosamente.')
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'cliente_form.html', {'form': form, 'cliente_id': cliente_id})

def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, cliente_id=cliente_id)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, f'Cliente {cliente_id} eliminado exitosamente.')
        return redirect('lista_clientes')
    return render(request, 'eliminar_cliente.html', {'cliente': cliente})
    #return render(request, 'confirmar_eliminar_cli.html', {'cliente': cliente})

def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, cliente_id=cliente_id)
    return render(request, 'detalle_cliente.html', {
        'cliente': cliente,
        'cliente_id': cliente_id
    })


def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                usuario = form.save()
                login(request, usuario)
                cliente = usuario.cliente
                messages.success(request, f'¡Registro exitoso! Tu ID de cliente es {cliente.cliente_id}')
                
                # Verificar si hay un producto pendiente para agregar al carrito
                producto_id = request.session.pop('producto_a_agregar', None)
                if producto_id:
                    return redirect('agregar_al_carrito', producto_id=producto_id)
                
                return redirect('perfil_cliente')
    else:
        form = RegistroClienteForm()
    
    return render(request, 'portal/registro.html', {'form': form})

@login_required
def perfil_cliente(request):
    try:
        cliente = request.user.cliente
        return render(request, 'portal/perfil.html', {
            'cliente': cliente,
            'cliente_id': cliente.cliente_id
        })
    except AttributeError:
        messages.error(request, 'No tienes un perfil de cliente asociado')
        return redirect('registro_cliente')


    carrito = request.session.get('carrito', {})
    
    for producto_id, item in carrito.items():
        item['subtotal'] = float(item['precio']) * float(item['cantidad'])
    
    if request.method == 'POST' and 'confirmar_pedido' in request.POST:
        if not carrito:
            messages.error(request, 'Tu carrito está vacío')
            return redirect('carrito_compras')
            
        with transaction.atomic():
            venta = Venta.objects.create(
                cliente=request.user,
                estatus_venta='Pendiente'
            )
            
            for producto_id, item in carrito.items():
                producto = get_object_or_404(Producto, pk=producto_id)
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=item['cantidad'],
                    unidad_medida=item['unidad_medida'],
                    precio_unitario=producto.precio_unitario
                )
            
            request.session['carrito'] = {}
            messages.success(request, f'¡Pedido #{venta.venta_id} realizado con éxito!')
            return redirect('portal/historial')
    
    return render(request, 'portal/carrito.html', {
        'carrito': carrito,
        'total_general': sum(item['subtotal'] for item in carrito.values())
    })

def agregar_al_carrito(request, producto_id):
    if not request.user.is_authenticated:
        request.session['producto_a_agregar'] = producto_id
        messages.warning(request, 'Debes iniciar sesión para agregar productos')
        return redirect('registro_cliente')
    
    producto = get_object_or_404(Producto, producto_id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))

    # Validar stock disponible
    if cantidad > producto.cantidad_disponible:
        messages.error(
            request, 
            f'No hay suficientes galletas de {producto.nombre}. '
            f'Quedan {producto.cantidad_disponible} unidades disponibles.'
        )
        return redirect('catalogo')

    carrito = request.session.get('carrito', {})

    if str(producto_id) in carrito:
        # Validar que al sumar no exceda el stock
        nueva_cantidad = carrito[str(producto_id)]['cantidad'] + cantidad
        if nueva_cantidad > producto.cantidad_disponible:
            disponibles = producto.cantidad_disponible - carrito[str(producto_id)]['cantidad']
            msg = (f'Solo puedes agregar {disponibles} más de {producto.nombre} ' 
                   f'(hay {producto.cantidad_disponible} disponibles)')
            messages.warning(request, msg)
            return redirect('catalogo')
        carrito[str(producto_id)]['cantidad'] = nueva_cantidad
    else:
        carrito[str(producto_id)] = {
            'nombre': producto.nombre,
            'precio_unitario': str(producto.precio_unitario),
            'cantidad': cantidad,
            'unidad_medida': producto.unidad_medida,
        }

    request.session['carrito'] = carrito
    messages.success(request, f'"{producto.nombre}" agregado al carrito')
    return redirect('catalogo')





def catalogo(request):
    productos = Producto.objects.all()
    return render(request, 'carrito/catalogo.html', {'productos': productos})



@login_required
def carrito(request):
    carrito_items = Carrito.objects.filter(cliente=request.user.cliente)
    total = sum(item.producto.precio_unitario * item.cantidad for item in carrito_items)
    total_con_impuesto = total * Decimal(1.16)  
    
    return render(request, 'carrito/carrito.html', {'carrito_items': carrito_items, 'total': total_con_impuesto})

@login_required
def confirmar_venta(request):
    carrito_items = Carrito.objects.filter(cliente=request.user.cliente)
    total = sum(item.producto.precio_unitario * item.cantidad for item in carrito_items)
    
    # Crear venta
    venta = Venta(persona=request.user.cliente, estatus_venta='Pendiente')
    venta.save()
    
    # Crear detalles de venta
    for item in carrito_items:
        detalle = DetalleVenta(
            venta=venta,
            producto=item.producto,
            cantidad=item.cantidad,
            unidad_medida=item.unidad_medida,
            precio_unitario=item.producto.precio_unitario
        )
        detalle.save()

    # Vaciar el carrito
    carrito_items.delete()
    
    return redirect('carrito/historial_compras')



@login_required
def generar_ticket_reportlab(request, venta_id):
    venta = Venta.objects.get(id=venta_id)
    detalles = venta.detalles.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{venta.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # --- SECCIÓN: ENCABEZADO ---
    encabezado_data = [
        [Paragraph("<b>Ticket de Venta</b>", styles["Title"])],
        [Paragraph(f"<b>ID:</b> {venta.id}", styles["Normal"])],
        [Paragraph(f"<b>Cliente:</b> {venta.persona.nombre}", styles["Normal"])],
        [Paragraph(f"<b>Fecha:</b> {venta.fecha_venta.strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"])],
        [Paragraph(f"<b>Estado:</b> {venta.estatus_venta}", styles["Normal"])],
    ]

    encabezado_tabla = Table(encabezado_data, colWidths=[5.5 * inch])
    encabezado_tabla.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(encabezado_tabla)
    elements.append(Spacer(1, 0.3 * inch))  

    # --- SECCIÓN: DETALLES DE PRODUCTOS ---
    elements.append(Paragraph("<b>Detalles de la Compra</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    data = [["Producto", "Cantidad", "Precio Unitario", "Total"]]
    for detalle in detalles:
        data.append([
            detalle.producto.nombre,
            f"{detalle.cantidad:.2f}",  
            f"${detalle.precio_unitario:.2f}",
            f"${detalle.precio_unitario * detalle.cantidad:.2f}"
        ])

    tabla = Table(data, colWidths=[2.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
    ]))

    elements.append(tabla)
    elements.append(Spacer(1, 0.3 * inch))

    # --- SECCIÓN: TOTAL GENERAL ---
    total = sum(detalle.precio_unitario * detalle.cantidad for detalle in detalles)

    total_data = [["", "", "Total a Pagar:", f"${total:.2f}"]]
    total_table = Table(total_data, colWidths=[2.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
    total_table.setStyle(TableStyle([
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (2, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, 0), (-1, -1), 14),
        ('TEXTCOLOR', (2, 0), (-1, -1), colors.black),
        ('TOPPADDING', (2, 0), (-1, -1), 10),
        ('BACKGROUND', (2, 0), (-1, -1), colors.yellow),
    ]))

    elements.append(total_table)

    doc.build(elements)

    return response


@login_required
def limpiar_carrito(request):
    # Eliminar el carrito de la sesión
    request.session['carrito'] = {}
    return redirect('ver_carrito')


@login_required
def eliminar_del_carrito(request, item_id):
    carrito = request.session.get("carrito", {})

    if str(item_id) in carrito:
        del carrito[str(item_id)]
        request.session["carrito"] = carrito  # Guardar cambios en la sesión

    return redirect("carrito/carrito")

@login_required
def actualizar_carrito(request, item_id):
    if request.method == "POST":
        try:
            nueva_cantidad = int(request.POST.get("cantidad"))
            if nueva_cantidad <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Cantidad debe ser un número positivo")
            return redirect('ver_carrito')

        producto = get_object_or_404(Producto, producto_id=item_id)
        carrito = request.session.get("carrito", {})

        if str(item_id) in carrito:
            # Validar stock disponible
            if nueva_cantidad > producto.cantidad_disponible:
                messages.error(
                    request,
                    f'No hay suficientes galletas de {producto.nombre}. '
                    f'Quedan {producto.cantidad_disponible} unidades disponibles.'
                )
                return redirect('ver_carrito')
            
            carrito[str(item_id)]["cantidad"] = nueva_cantidad
            request.session["carrito"] = carrito
            messages.success(request, "Cantidad actualizada correctamente")

    return redirect('ver_carrito')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from decimal import Decimal
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib import colors
from .models import Venta, DetalleVenta
from productos_app.models import Producto

@login_required
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    productos_sin_stock = []
    total = 0
    
    # Verificar stock y calcular total
    for item_id, item in carrito.items():
        producto = Producto.objects.get(producto_id=item_id)
        item['subtotal'] = float(item['precio_unitario']) * float(item['cantidad'])
        total += item['subtotal']
        
        # Verificar stock
        if item['cantidad'] > producto.cantidad_disponible:
            productos_sin_stock.append({
                'nombre': producto.nombre,
                'disponible': producto.cantidad_disponible,
                'solicitado': item['cantidad']
            })
    
    # Mostrar mensajes de stock insuficiente
    for producto in productos_sin_stock:
        messages.warning(
            request,
            f'No hay suficientes galletas de {producto["nombre"]}. '
            f'Quedan {producto["disponible"]} unidades (solicitadas: {producto["solicitado"]})'
        )
    
    return render(request, 'carrito/carrito.html', {
        'carrito': carrito,
        'total': total,
        'fecha_pedido': timezone.now().strftime("%d/%m/%Y %H:%M"),
        'bloquear_compra': len(productos_sin_stock) > 0
    })

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect, reverse  # Añade reverse aquí
from decimal import Decimal
from .models import Venta, DetalleVenta
from productos_app.models import Producto

@login_required
def confirmar_compra(request):
    carrito = request.session.get('carrito', {})
    
    if not carrito:
        return redirect('ver_carrito')

    # Validar stock antes de procesar la compra
    productos_sin_stock = []
    for item_id, item in carrito.items():
        producto = Producto.objects.get(producto_id=item_id)
        if item['cantidad'] > producto.cantidad_disponible:
            productos_sin_stock.append({
                'nombre': producto.nombre,
                'disponible': producto.cantidad_disponible,
                'solicitado': item['cantidad']
            })

    if productos_sin_stock:
        for producto in productos_sin_stock:
            messages.error(
                request, 
                f"No hay suficientes galletas de {producto['nombre']}. "
                f"Quedan {producto['disponible']} unidades disponibles."
            )
        return redirect('ver_carrito')

    # Procesar la compra si todo está bien
    try:
        with transaction.atomic():
            venta = Venta(
                persona=request.user.cliente,
                estatus_venta='Pagado',
                estado_entrega='entregado',
                metodo_pago='efectivo'
            )
            venta.save()

            for item_id, item in carrito.items():
                producto = Producto.objects.get(producto_id=item_id)
                
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=item['cantidad'],
                    unidad_medida=item.get('unidad_medida', 'pz'),
                    precio_unitario=item['precio_unitario']
                )

                producto.cantidad_disponible -= Decimal(item['cantidad'])
                producto.save()

            # Vaciar carrito
            request.session['carrito'] = {}
            
            # Guardar el ID de la venta en la sesión para mostrar el mensaje
            request.session['venta_reciente'] = venta.id
            return redirect('historial_compras')

    except Exception as e:
        messages.error(request, f'Ocurrió un error al procesar tu compra: {str(e)}')
        return redirect('ver_carrito')

@login_required
def generar_ticket(request, venta_id):
    try:
        venta = get_object_or_404(Venta, id=venta_id, persona__usuario=request.user)
        detalles = venta.detalles.select_related('producto').all()
        
        # Calcular subtotales y total
        for detalle in detalles:
            detalle.subtotal = float(detalle.precio_unitario) * float(detalle.cantidad)
        total = sum(d.subtotal for d in detalles)
        
        # Si se solicita descarga PDF
        if 'download' in request.GET:
            return generar_pdf(request, venta, detalles, total)
        
        # Vista normal HTML
        context = {
            'venta': venta,
            'detalles': detalles,
            'total': total,
            'fecha': venta.fecha_venta.strftime("%d/%m/%Y %H:%M")
        }
        return render(request, 'carrito/ticket.html', context)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise Http404("Error al generar el ticket")

from reportlab.lib.units import mm
from reportlab.lib import colors

def generar_pdf(request, venta, detalles, total):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{venta.id}.pdf"'
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=(80*mm, 200*mm))
    
    # Configuración inicial
    width, height = 80*mm, 200*mm
    y_position = height - 10*mm  # Comenzamos desde la parte superior
    
    # Encabezado
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width/2, y_position, "DON GALLETITA")
    y_position -= 8*mm
    
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, y_position, "Universidad Tecnologica de Leon")
    y_position -= 5*mm
    p.drawCentredString(width/2, y_position, "San Carlos, la roncha")
    y_position -= 5*mm
    p.drawCentredString(width/2, y_position, "Leon Guanajuato")
    y_position -= 10*mm
    
    # Línea divisoria
    p.line(5*mm, y_position, width-5*mm, y_position)
    y_position -= 8*mm
    
    # Datos del cliente
    p.setFont("Helvetica-Bold", 10)
    p.drawString(10*mm, y_position, f"Cliente: {venta.persona.nombre}")
    y_position -= 6*mm
    p.drawString(10*mm, y_position, f"Ticket: {venta.id}")
    y_position -= 6*mm
    
    # Estado de pago y entrega (MODIFICADO PARA MOSTRAR CORRECTAMENTE)
    estado_pago = "Pagado" if venta.estatus_venta == 'Pagado' else "Pendiente"
    p.drawString(10*mm, y_position, f"Pago: {estado_pago}")
    y_position -= 6*mm
    p.drawString(10*mm, y_position, f"Entrega: {venta.estado_entrega.capitalize()}")
    y_position -= 10*mm
    
    # Línea divisoria
    p.line(5*mm, y_position, width-5*mm, y_position)
    y_position -= 8*mm
    
    # Tabla de productos
    p.setFont("Helvetica-Bold", 10)
    p.drawString(10*mm, y_position, "Producto")
    p.drawString(40*mm, y_position, "Cant")
    p.drawString(50*mm, y_position, "Precio")
    p.drawString(65*mm, y_position, "Total")
    y_position -= 6*mm
    
    p.setFont("Helvetica", 9)
    for detalle in detalles:
        # Ajuste para evitar salto de página
        if y_position < 30*mm:
            p.showPage()
            y_position = height - 10*mm
            p.setFont("Helvetica", 9)
        
        p.drawString(10*mm, y_position, detalle.producto.nombre[:15])  # Limitar longitud del nombre
        p.drawString(40*mm, y_position, f"{detalle.cantidad} {detalle.unidad_medida}")
        p.drawString(50*mm, y_position, f"${detalle.precio_unitario:.2f}")
        p.drawString(65*mm, y_position, f"${detalle.subtotal:.2f}")
        y_position -= 6*mm
    
    # Línea divisoria
    y_position -= 4*mm
    p.line(5*mm, y_position, width-5*mm, y_position)
    y_position -= 8*mm
    
    # Total
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40*mm, y_position, "TOTAL:")
    p.drawString(65*mm, y_position, f"${total:.2f}")
    y_position -= 12*mm
    
    # Fecha
    p.setFont("Helvetica", 9)
    p.drawCentredString(width/2, y_position, f"Fecha: {venta.fecha_venta.strftime('%d/%m/%Y %H:%M')}")
    y_position -= 10*mm
    
    # Mensaje final
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, y_position, "¡Gracias por su compra!")
    y_position -= 6*mm
    p.drawCentredString(width/2, y_position, "Por favor vuelva pronto")
    y_position -= 6*mm
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width/2, y_position, "Don Galletita")
    
    # Finalizar PDF
    p.showPage()
    p.save()
    
    # Obtener PDF y cerrar buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Escribir en la respuesta
    response.write(pdf)
    return response

@login_required
def historial_compras(request):
    ventas = Venta.objects.filter(
        persona__usuario=request.user
    ).prefetch_related('detalles__producto').order_by('-fecha_venta')
    
    ventas_con_detalle = []
    for venta in ventas:
        detalles = venta.detalles.all()
        total = sum(d.precio_unitario * d.cantidad for d in detalles)
        ventas_con_detalle.append({
            'venta': venta,
            'detalles': detalles,
            'total': total,
            'fecha': venta.fecha_venta.strftime("%d/%m/%Y %H:%M")
        })
    
    return render(request, 'carrito/historial_compras.html', {
        'ventas_con_detalle': ventas_con_detalle
    })
