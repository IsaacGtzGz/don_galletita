from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from .models import Cliente, Producto, Venta, DetalleVenta
from .forms import RegistroClienteForm, CarritoForm, ClienteForm
from usuarios_app.models import Usuario
from django.core.exceptions import ObjectDoesNotExist

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

# Portal del Cliente
def puede_comprar(user):
    return hasattr(user, 'rol') and user.rol in ['cliente', 'admin']


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
            return redirect('historial_compras')
    
    return render(request, 'portal/carrito.html', {
        'carrito': carrito,
        'total_general': sum(item['subtotal'] for item in carrito.values())
    })

@login_required
def agregar_al_carrito(request):
    if request.method == 'POST':
        form = CarritoForm(request.POST)
        if form.is_valid():
            producto_id = str(form.cleaned_data['producto_id'])
            producto = get_object_or_404(Producto, pk=producto_id)
            
            carrito = request.session.get('carrito', {})
            
            if producto_id in carrito:
                carrito[producto_id]['cantidad'] += form.cleaned_data['cantidad']
            else:
                carrito[producto_id] = {
                    'nombre': producto.nombre,
                    'unidad_medida': form.cleaned_data['unidad_medida'],
                    'cantidad': float(form.cleaned_data['cantidad']),
                    'precio': float(producto.precio_unitario)
                }
            
            request.session['carrito'] = carrito
            messages.success(request, 'Producto añadido al carrito')
    
    return redirect('carrito_compras')

@login_required
def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session['carrito'] = carrito
        messages.success(request, 'Producto eliminado del carrito')
    return redirect('carrito_compras')


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

@compra_permitida
def historial_compras(request):
    try:
        cliente = request.user.cliente
        ventas = Venta.objects.filter(cliente=request.user).order_by('-fecha_venta')
        return render(request, 'portal/historial.html', {'ventas': ventas})
    except ObjectDoesNotExist:
        messages.error(request, 'No tienes un perfil de cliente asociado')
        return redirect('registro_cliente')  



@compra_permitida
def carrito_compras(request):
    try:
        # Verificar que el usuario tenga perfil de cliente
        request.user.cliente
        carrito = request.session.get('carrito', {})
        
        # Resto de la lógica del carrito...
        return render(request, 'portal/carrito.html', {
            'carrito': carrito,
            'total_general': sum(item['subtotal'] for item in carrito.values())
        })
    except ObjectDoesNotExist:
        messages.error(request, 'No tienes un perfil de cliente asociado')
        return redirect('inicio')
    ventas = Venta.objects.filter(cliente=request.user).order_by('-fecha_venta')
    return render(request, 'portal/historial.html', {
        'ventas': ventas,
        'cliente_id': request.user.cliente.cliente_id
    })

@compra_permitida
def cancelar_pedido(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id, cliente=request.user)
    if venta.estatus_venta == 'Pendiente':
        venta.estatus_venta = 'Cancelado'
        venta.save()
        messages.success(request, f'Pedido #{venta_id} cancelado exitosamente')
    else:
        messages.error(request, 'Solo puedes cancelar pedidos pendientes')
    return redirect('historial_compras')