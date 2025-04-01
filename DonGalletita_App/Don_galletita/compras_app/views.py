from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from django.urls import reverse_lazy
from . import forms
from .models import Compra

# Listar compras
class ListaComprasView(TemplateView):
    template_name = 'lista_compras.html'

    def get_context_data(self):
        lista = Compra.objects.all()
        return {'lista': lista}
    
# Crear una compra
class CrearCompraView(FormView):
    template_name = 'crear_compra.html'  
    form_class = forms.CompraRegistrarForm
    success_url = reverse_lazy('lista_compras')

    def form_valid(self, form):
        form.save(self.request)
        return super().form_valid(form)
    
# Editar una compra    
class EditarCompraView(FormView):
    template_name = 'editar_compra.html'  
    form_class = forms.CompraEditarForm
    success_url = reverse_lazy('lista_compras')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        id = self.kwargs.get('id')
        compra = get_object_or_404(Compra, compra_id=id)
        kwargs['instance'] = compra
        return kwargs
    
    def form_valid(self, form):
        id = self.kwargs.get('id')
        form.save(id=id)
        return super().form_valid(form)
