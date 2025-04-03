from django.shortcuts import render, get_object_or_404
from insumos_app.models import Insumos
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from django.views.generic.edit import DeleteView
from . import forms
from django.urls import reverse_lazy

# Create your views here.

class ListaInsumoView(TemplateView):
    template_name = 'lista_insumo.html' 
    def get_context_data(self):
        insumos = Insumos.objects.all()
        return {
            'insumos': insumos
        }
    
class CrearInsumoView(FormView):
    template_name = 'crear_insumo.html'
    form_class = forms.InsumosRegistrarForm
    success_url = reverse_lazy('lista_insumo')
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    

class EditarInsumoView(FormView):
    template_name = 'editar_insumo.html'
    form_class = forms.InsumosEditarForm
    success_url = reverse_lazy('lista_insumo')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        insumo_id = self.kwargs.get('insumo_id')
        insumos = get_object_or_404(Insumos, id=insumo_id)
        kwargs['instance'] = insumos
        return kwargs
    
    def form_valid(self, form):
        # Obtener el insumo del formulario y la unidad actual
        insumo = form.instance
        nueva_unidad = form.cleaned_data.get('unidad_medida')
        print(f"Datos limpios: Cantidad: {insumo.cantidad_disponible}, Unidad: {insumo.unidad_medida}")
        print(f"Cantidad antes de guardar: {insumo.cantidad_disponible} {insumo.unidad_medida}")
        
        # Convertir la unidad si es necesario
        if insumo.unidad_medida != nueva_unidad:
            insumo.convertir_unidad(nueva_unidad)
        
        insumo.save()
        print(f"Cantidad después de guardar: {insumo.cantidad_disponible} {insumo.unidad_medida}")
        return super().form_valid(form)

class EliminarInsumoView(DeleteView):
    model = Insumos
    template_name = 'eliminar_insumo.html'
    success_url = reverse_lazy('lista_insumo')
