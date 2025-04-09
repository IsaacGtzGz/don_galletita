from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import JsonResponse
from .models import Producto
from .forms import ProductoForm
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

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

        # Obtener productos con lotes próximos a caducar
        from produccion_app.models import LoteProduccion
        lotes_por_caducar = LoteProduccion.objects.filter(
            fecha_caducidad__lte=alerta_fecha,
            estado='disponible'
        ).select_related('produccion__receta__producto')
    
        # Crear estructura para mostrar en template
        productos_alerta = {}
        for lote in lotes_por_caducar:
            producto = lote.produccion.receta.producto
            if producto not in productos_alerta:
                productos_alerta[producto] = {
                    'cantidad': 0,
                    'fecha_caducidad': lote.fecha_caducidad
                }
            productos_alerta[producto]['cantidad'] += lote.cantidad_galletas
        
        context['productos_proximos_caducar'] = productos_alerta
        context['fecha_actual'] = hoy
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
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # ¡Forzar la carga de la instancia existente!
        kwargs['instance'] = self.get_object()  
        return kwargs
    
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

def obtener_precio_producto(request, producto_id):
    try:
        producto = Producto.objects.get(producto_id=producto_id)  # Cambiado de 'id' a 'producto_id'
        return JsonResponse({'precio': producto.precio_unitario})
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
