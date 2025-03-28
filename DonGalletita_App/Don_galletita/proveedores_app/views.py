from django.shortcuts import get_object_or_404, redirect
from proveedores_app.models import Proveedor
from django.views.generic.base import TemplateView
from django.views.generic import FormView, DeleteView
from . import forms
from django.urls import reverse_lazy

# Create your views here.
class ListaProveedoresView(TemplateView):
    template_name = 'lista_proveedores.html'

    def get_context_data(self):
        lista = Proveedor.objects.all()
        return {'lista': lista}
    
# Crear un proveedor
class CrearProveedorView(FormView):
    template_name = 'crear_proveedor.html'  
    form_class = forms.ProveedorRegistrarForm
    success_url = reverse_lazy('lista_proveedores')
    def form_valid(self, form):
        form.save(self.request)
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
        kwargs['instance'] = proveedor
        return kwargs
    
    def form_valid(self, form):
        id = self.kwargs.get('id')
        form.save(id=id)
        return super().form_valid(form)

# Eliminar un proveedor
class EliminarProveedorView(DeleteView):
    model = Proveedor
    template_name = 'eliminar_proveedor.html'
    success_url = reverse_lazy('lista_proveedores')

    def get_object(self, queryset=None):
        id = self.kwargs.get('id')
        return get_object_or_404(Proveedor, proveedor_id=id)
