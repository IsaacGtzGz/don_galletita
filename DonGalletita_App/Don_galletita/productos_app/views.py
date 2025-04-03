from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Producto
from .forms import ProductoForm
from datetime import timedelta

class ListaProductosView(ListView):
    model = Producto
    template_name = 'lista_productos.html'
    context_object_name = 'productos'
    ordering = ['nombre']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Inventario de Productos'
        hoy = timezone.now().date()
        alerta_fecha = hoy + timedelta(days=2)
        context['fecha_actual'] = timezone.now().date()
    
        productos_por_caducar = Producto.objects.filter(fecha_caducidad=alerta_fecha)
        
        context['productos_por_caducar'] = productos_por_caducar
        return context

class CrearProductoView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'crear_producto.html'
    success_url = reverse_lazy('lista_productos')
    success_message = "Producto registrado exitosamente"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar nuevo producto'
        context['accion'] = 'crear'
        return context

class EditarProductoView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'editar_producto.html'
    success_url = reverse_lazy('lista_productos')
    success_message = "Producto actualizado exitosamente"
    pk_url_kwarg = 'producto_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar {self.object.nombre}'
        context['accion'] = 'editar'
        return context

class EliminarProductoView(DeleteView):
    model = Producto
    template_name = 'eliminar_producto.html'
    success_url = reverse_lazy('lista_productos')
    success_message = "Producto eliminado exitosamente"
    pk_url_kwarg = 'producto_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Eliminar {self.object.nombre}'
        return context

