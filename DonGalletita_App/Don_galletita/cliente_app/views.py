from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
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
    producto = Producto.objects.get(producto_id=producto_id)  # Asegúrate de usar el campo correcto
    cantidad = int(request.POST.get('cantidad', 1))  # Obtiene la cantidad del formulario, por defecto 1

    carrito = request.session.get('carrito', {})

    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += cantidad  # Incrementa por la cantidad seleccionada
    else:
        carrito[str(producto_id)] = {
            'nombre': producto.nombre,
            'precio_unitario': str(producto.precio_unitario),  # Guarda como string para evitar problemas
            'cantidad': cantidad,  # Usa la cantidad seleccionada por el usuario
        }

    request.session['carrito'] = carrito  # Guarda el carrito en la sesión
    request.session.modified = True  # Asegura que Django guarde los cambios
    print("Carrito después de agregar:", request.session['carrito'])  # <-- Agrega este print para ver si se guarda

    return redirect('ver_carrito')





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
def historial_compras(request):
    ventas = Venta.objects.filter(persona__usuario=request.user).prefetch_related("detalles").order_by('-fecha_venta')

    for venta in ventas:
        venta.total = sum(detalle.precio_unitario * detalle.cantidad for detalle in venta.detalles.all())

    return render(request, 'carrito/historial_compras.html', {'ventas': ventas})


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
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    total = 0

    for item in carrito.values():
        precio = float(item['precio_unitario'])
        cantidad = int(item['cantidad'])
        total += precio * cantidad

    # 🔥 Verifica qué datos tiene el carrito antes de renderizar la vista
    print("📦 Contenido del carrito:", carrito)

    return render(request, 'carrito/carrito.html', {'carrito': carrito, 'total': total})

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
        nueva_cantidad = request.POST.get("cantidad")

        # Validar que la cantidad es un número válido
        try:
            nueva_cantidad = Decimal(nueva_cantidad)
            if nueva_cantidad <= 0:
                raise ValueError("Cantidad inválida")
        except (ValueError, TypeError):
            return redirect("carrito_compras")  # Redirigir sin cambios si la cantidad es inválida

        carrito = request.session.get("carrito", {})

        if str(item_id) in carrito:
            carrito[str(item_id)]["cantidad"] = float(nueva_cantidad)  # Guardar como número

        request.session["carrito"] = carrito  # Guardar cambios en la sesión

    return redirect("carrito/carrito") 

@login_required
def confirmar_compra(request):
    # Obtener el carrito desde la sesión
    carrito = request.session.get('carrito', {})

    if not carrito:
        # Si el carrito está vacío, redirigir al carrito
        return redirect('ver_carrito')

    # Crear la venta con estado "Pagado" directamente
    venta = Venta(persona=request.user.cliente, estatus_venta='Pagada')
    venta.save()  # Guarda la venta

    # Agregar los productos del carrito a la venta
    for item_id, item in carrito.items():
        producto_id = item_id  # El ID del producto (clave del carrito)
        producto = Producto.objects.get(producto_id=producto_id)  # Obtener el producto del carrito

        # Crear el detalle de la venta (esto guarda cada producto vendido)
        detalle = DetalleVenta(
            venta=venta,
            producto=producto,
            cantidad=item['cantidad'],
            precio_unitario=item['precio_unitario']
        )
        detalle.save()  # Guarda el detalle de la venta

        # Actualizar el inventario
        producto.cantidad_disponible -= item['cantidad']
        producto.save()

    # Vaciar el carrito después de la compra
    request.session['carrito'] = {}

    # Redirigir al historial de compras
    messages.success(request, f'¡Compra confirmada y pagada exitosamente!')

    return redirect('historial_compras')
