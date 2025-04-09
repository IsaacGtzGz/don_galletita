from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic import FormView, DeleteView
from django.urls import reverse_lazy
from insumos_app.models import Insumos
from . import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.html import escape
import logging

logger = logging.getLogger(__name__)

# Lista de insumos
class ListaInsumoView(LoginRequiredMixin, TemplateView):
    template_name = 'lista_insumo.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = escape(self.request.GET.get('q', ''))  # Obtén el parámetro de búsqueda
        if query:
            # Filtra los insumos cuyo nombre contiene el texto ingresado
            context['insumos'] = Insumos.objects.filter(nombre__icontains=query)
        else:
            # Muestra todos los insumos si no hay búsqueda
            context['insumos'] = Insumos.objects.all()
        return context

# Crear un insumo
class CrearInsumoView(LoginRequiredMixin, FormView):
    template_name = 'crear_insumo.html'
    form_class = forms.InsumosRegistrarForm
    success_url = reverse_lazy('lista_insumo')
    login_url = 'login'

    def form_valid(self, form):
        form.save()  # Guarda el formulario sin pasar un id
        return super().form_valid(form)

# Editar un insumo
class EditarInsumoView(LoginRequiredMixin, FormView):
    template_name = 'editar_insumo.html'
    form_class = forms.InsumosEditarForm
    success_url = reverse_lazy('lista_insumo')
    login_url = 'login'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        insumo_id = self.kwargs.get('insumo_id')
        insumo = get_object_or_404(Insumos, id=insumo_id)
        kwargs['instance'] = insumo  # Pasar la instancia al formulario
        return kwargs

    def form_valid(self, form):
        form.save()  # Guarda los cambios en la instancia del modelo
        return super().form_valid(form)

# Eliminar un insumo
class EliminarInsumoView(LoginRequiredMixin, DeleteView):
    model = Insumos
    template_name = 'eliminar_insumo.html'
    success_url = reverse_lazy('lista_insumo')
    login_url = 'login'

    def get_object(self):
        insumo_id = self.kwargs.get('insumo_id')
        return get_object_or_404(Insumos, id=insumo_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        insumo = self.get_object()
        context['titulo'] = 'Eliminar Insumo'
        context['mensaje'] = '¿Estás seguro de que deseas eliminar este insumo?'
        context['url_cancelar'] = reverse_lazy('lista_insumo')
        return context

    def form_valid(self, form):
        insumo_id = self.kwargs.get('insumo_id')
        insumo = get_object_or_404(Insumos, id=insumo_id)
        logger.info(f'Insumo eliminado con ID: {insumo_id} por {self.request.user}')
        return super().form_valid(form)