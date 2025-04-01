from django.shortcuts import render, get_object_or_404
from insumos_app.models import Insumos
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from django.views.generic.edit import DeleteView
from . import forms
from django.urls import reverse_lazy
from datetime import date, timedelta

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
        insumo = form.save()
        print(f"Cantidad después de guardar: {insumo.cantidad_disponible} {insumo.unidad_medida}")
        return super().form_valid(form)

class EliminarInsumoView(DeleteView):
    model = Insumos
    template_name = 'confirmar_eliminar.html'
    success_url = reverse_lazy('lista_insumo')

def agregar_al_carrito(request, detalle):
    if 'carrito' not in request.session:
        request.session['carrito'] = []
    request.session['carrito'].append({
        'insumo': detalle['insumo'].id,  # Usa .id para obtener el identificador
        'nombre_insumo': detalle['insumo'].nombre_insumo,
        'cantidad': detalle['cantidad'],
        'precio_unitario': detalle['precio_unitario'],
        'unidad_medida': detalle['unidad_medida'],  # Agregar unidad de medida
        'fecha_caducidad': detalle['fecha_caducidad'].strftime('%Y-%m-%d') if detalle['fecha_caducidad'] else None,
    })

def listar_insumos(request):
    insumos = Insumos.objects.all()
    proximos_a_caducar = insumos.filter(fecha_caducidad__lte=date.today() + timedelta(days=7))
    return render(request, 'lista_insumo.html', {
        'insumos': insumos,
        'proximos_a_caducar': proximos_a_caducar
    })

def alertas_caducidad(request):
    proximos_a_caducar = Insumos.objects.filter(
        fecha_caducidad__lte=date.today() + timedelta(days=7),
        fecha_caducidad__gte=date.today()
    )
    return render(request, 'alertas_caducidad.html', {'proximos_a_caducar': proximos_a_caducar})