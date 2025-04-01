from django.shortcuts import render, redirect, get_object_or_404
import json
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
from .models import Venta, Producto


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
    return render(request, 'confirmar_eliminar_cli.html', {'cliente': cliente})

def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, cliente_id=cliente_id)
    return render(request, 'detalle_cliente.html', {
        'cliente': cliente,
        'cliente_id': cliente_id
    })

# Portal del Cliente
def puede_comprar(user):
    return hasattr(user, 'rol') and user.rol in ['cliente', 'admin']

@login_required
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    
    # Calcular subtotales y total
    for item in carrito.values():
        item['subtotal'] = item['precio'] * item['cantidad']
    
    total = sum(item['subtotal'] for item in carrito.values())
    
    return render(request, 'portal/carrito.html', {
        'carrito': carrito,
        'total': total
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


@login_required
def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    
    if str(producto_id) in carrito:
        producto_nombre = carrito[str(producto_id)]['nombre']
        del carrito[str(producto_id)]
        request.session['carrito'] = carrito
        request.session.modified = True
        messages.success(request, f'{producto_nombre} eliminado del carrito')
    else:
        messages.error(request, 'Producto no encontrado en el carrito')
    
    return redirect('ver_carrito')


def compra_permitida(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder')
            return redirect('login')  # Usar 'login' que es estándar en Django
            
        try:
            request.user.cliente
            return view_func(request, *args, **kwargs)
        except ObjectDoesNotExist:
            messages.error(request, 'No tienes un perfil de cliente válido')
            return redirect('registro_cliente') 
    return _wrapped_view

@login_required
def historial_compras(request):
    # Obtener el cliente asociado al usuario actual
    cliente_actual = request.user.cliente  # Asume que ya tienes esta relación
    
    # Filtrar ventas por el cliente actual
    ventas = Venta.objects.filter(cliente=cliente_actual).order_by('-fecha_creacion')
    
    return render(request, 'portal/historial.html', {
        'ventas': ventas,
        'cliente': cliente_actual
    })

@login_required
def actualizar_carrito(request, producto_id):
    if request.method == 'POST':
        cantidad = float(request.POST.get('cantidad', 1))
        
        try:
            producto = Producto.objects.get(pk=producto_id)
            carrito = request.session.get('carrito', {})
            
            if str(producto_id) in carrito:
                if cantidad <= 0:
                    del carrito[str(producto_id)]
                    messages.success(request, 'Producto eliminado del carrito')
                else:
                    # Validar disponibilidad
                    if cantidad > producto.cantidad_disponible:
                        messages.error(request, 'No hay suficiente stock disponible')
                    else:
                        carrito[str(producto_id)]['cantidad'] = cantidad
                        messages.success(request, 'Cantidad actualizada')
                
                request.session['carrito'] = carrito
                request.session.modified = True
            
        except Producto.DoesNotExist:
            messages.error(request, 'Producto no encontrado')
    
    return redirect('ver_carrito')


def cancelar_pedido(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id, cliente=request.user)
    
    if venta.estatus_venta == 'Pendiente':
        try:
            with transaction.atomic():
                # Revertir stock
                for detalle in venta.detalles.all():
                    producto = detalle.producto
                    producto.cantidad_disponible += detalle.cantidad
                    producto.save()
                
                # Actualizar estado
                venta.estatus_venta = 'Cancelado'
                venta.save()
                
                messages.success(request, f'Pedido #{venta_id} cancelado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al cancelar el pedido: {str(e)}')
    else:
        messages.error(request, 'Solo puedes cancelar pedidos pendientes')
    
    return redirect('portal/historial')

@login_required
def confirmacion_pedido(request):
    return render(request, 'portal/confirmacion_pedido.html')


def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})
    
    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += 1
    else:
        carrito[str(producto_id)] = {
            'nombre': producto.nombre,
            'precio': str(producto.precio),  
            'cantidad': 1,
            'unidad_medida': producto.unidad_medida
        }
    
    request.session['carrito'] = carrito
    return redirect('ver_carrito')

@login_required
def carrito_compras(request):
    carrito = request.session.get('carrito', {})
    
    # Calcular totales
    total = 0
    for item in carrito.values():
        item['subtotal'] = item['precio'] * item['cantidad']
        total += item['subtotal']
    
    return render(request, 'portal/carrito.html', {
        'carrito': carrito,
        'total': total
    })

@login_required
def checkout(request):
    carrito = request.session.get('carrito', {})
    
    if not carrito:
        return redirect('ver_carrito')

    # Calcular total
    total = sum(float(item['precio']) * int(item['cantidad']) for item in carrito.values())
    
    if request.method == 'POST':
        try:
            # Crear la venta con los items en JSON
            venta = Venta.objects.create(
                cliente=request.user.cliente,
                direccion=request.POST.get('direccion'),
                metodo_pago=request.POST.get('metodo_pago'),
                total=total,
                items_json=json.dumps(carrito)  # Guarda todo el carrito como JSON
            )
            
            # Limpiar carrito
            del request.session['carrito']
            request.session.modified = True
            
            return redirect('portal/confirmacion_pedido', venta_id=venta.id)
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('portal/checkout')
    
    return render(request, 'portal/checkout.html', {
        'carrito': carrito,
        'total': total
    })