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

# Función para verificar roles permitidos
def puede_comprar(user):
    return hasattr(user, 'rol') and user.rol in ['cliente', 'admin']

# Decorador personalizado CORREGIDO
def compra_permitida(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not puede_comprar(request.user):
            messages.error(request, 'Solo clientes y administradores pueden acceder')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return login_required(_wrapped_view)

# CRUD Clientes
def lista_clientes(request):
    query = request.GET.get('q')
    clientes = Cliente.objects.filter(
        Q(nombre__icontains=query) |
        Q(apellido_paterno__icontains=query) |
        Q(apellido_materno__icontains=query) |
        Q(telefono__icontains=query)
    ) if query else Cliente.objects.all()
    paginator = Paginator(clientes.order_by('-fecha_registro'), 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'lista_clientes.html', {'page_obj': page_obj})

def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado exitosamente.')
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'cliente_form.html', {'form': form})

def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, cliente_id=id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'cliente_form.html', {'form': form})

def eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, cliente_id=id)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado exitosamente.')
        return redirect('lista_clientes')
    return render(request, 'confirmar_eliminar_cli.html', {'cliente': cliente})

def detalle_cliente(request, id):
    cliente = get_object_or_404(Cliente, cliente_id=id)
    return render(request, 'detalle_cliente.html', {'cliente': cliente})

# Portal del Cliente
def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, '¡Registro exitoso! Ahora puedes comprar.')
            return redirect('carrito_compras')
    else:
        form = RegistroClienteForm()
    return render(request, 'portal/registro.html', {'form': form})

@compra_permitida
def carrito_compras(request):
    carrito = request.session.get('carrito', {})
    
    # Calcular subtotales para cada producto
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
            messages.success(request, '¡Pedido realizado con éxito!')
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

@compra_permitida
def historial_compras(request):
    ventas = Venta.objects.filter(cliente=request.user).order_by('-fecha_venta')
    return render(request, 'portal/historial.html', {'ventas': ventas})

@compra_permitida
def cancelar_pedido(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id, cliente=request.user)
    if venta.estatus_venta == 'Pendiente':
        venta.estatus_venta = 'Cancelado'
        venta.save()
        messages.success(request, 'Pedido cancelado exitosamente')
    else:
        messages.error(request, 'Solo puedes cancelar pedidos pendientes')
    return redirect('historial_compras')