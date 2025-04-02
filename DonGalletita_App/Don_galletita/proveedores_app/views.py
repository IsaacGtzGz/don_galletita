from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic import FormView, DeleteView
from django.urls import reverse_lazy
from proveedores_app.models import Proveedor
from . import forms

# Lista de proveedores
class ListaProveedoresView(TemplateView):
    template_name = 'lista_proveedores.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')  # Obtén el parámetro de búsqueda
        if query:
            # Filtra los proveedores cuyo nombre contiene el texto ingresado
            context['lista'] = Proveedor.objects.filter(nombre__icontains=query)
        else:
            # Muestra todos los proveedores si no hay búsqueda
            context['lista'] = Proveedor.objects.all()
        return context

# Crear un proveedor
class CrearProveedorView(FormView):
    template_name = 'crear_proveedor.html'
    form_class = forms.ProveedorRegistrarForm
    success_url = reverse_lazy('lista_proveedores')

    def form_valid(self, form):
        form.save()  # Guarda el formulario sin pasar un id
        return super().form_valid(form)

# Editar un proveedor
class EditarProveedorView(FormView):
    template_name = 'editar_proveedor.html'
    form_class = forms.ProveedorEditarForm
    success_url = reverse_lazy('lista_proveedores')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        id = self.kwargs.get('id')
        proveedor = get_object_or_404(Proveedor, proveedor_id=id)
        kwargs['instance'] = proveedor  # Pasar la instancia al formulario
        return kwargs

    def form_valid(self, form):
        id = self.kwargs.get('id')  # Obtener el id de los argumentos de la URL
        form.save(id=id)  # Pasar el id requerido al método save
        return super().form_valid(form)

# Eliminar un proveedor
class EliminarProveedorView(DeleteView):
    model = Proveedor
    template_name = 'eliminar_proveedor.html'
    success_url = reverse_lazy('lista_proveedores')

    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(Proveedor, proveedor_id=id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proveedor = self.get_object()
        context['titulo'] = 'Eliminar Proveedor'
        context['mensaje'] = f'¿Estás seguro de que deseas eliminar al proveedor "{proveedor.nombre}"?'
        context['url_cancelar'] = reverse_lazy('lista_proveedores')
        return context
