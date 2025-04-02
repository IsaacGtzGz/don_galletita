from django.shortcuts import render, get_object_or_404
from receta_app.models import Receta, RecetaInsumo
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from django.views.generic.edit import DeleteView, UpdateView
from . import forms
from django.urls import reverse_lazy


class ListaRecetaView(TemplateView):
    template_name = 'lista_recetas.html' 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recetas'] = Receta.objects.all()
        return context
    
class CrearRecetaView(FormView):
    model = Receta
    template_name = 'crear_receta.html'
    form_class = forms.RecetasRegistrarForm
    success_url = reverse_lazy('lista_receta')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = forms.RecetasInsumoFormSet(
                self.request.POST, 
                self.request.FILES,
                prefix='insumos'
            )
        else:
            context['formset'] = forms.RecetasInsumoFormSet(
                prefix='insumos',
                queryset=RecetaInsumo.objects.none()  # No mostrar formularios existentes al crear
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save()  # Guarda primero la receta
            formset.instance = self.object
            formset.save()  # Luego guarda los insumos
            
            # Eliminar los marcados para borrado
            instances = formset.save(commit=False)
            for instance in instances:
                if instance.pk and formset.can_delete and formset._should_delete_form(formset.forms[instances.index(instance)]):
                    instance.delete()
            
            return super().form_valid(form)
        else:
            print("Errores en el formset:", formset.errors)
            return self.form_invalid(form)
        
    
class EditarRecetaView(UpdateView):
    model = Receta
    form_class = forms.RecetaEditarForm
    template_name = 'editar_receta.html'
    success_url = reverse_lazy('lista_receta')
    pk_url_kwarg = 'receta_id' #Para asegurar que se coinsida con el id

    def get_object(self, queryset=None):
        # Obtiene la receta específica usando receta_id
        receta_id = self.kwargs.get(self.pk_url_kwarg)
        return get_object_or_404(Receta, id=receta_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = forms.RecetasInsumoFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,  # ¡Esto es crucial!
                prefix='insumos'
            )
        else:
            context['formset'] = forms.RecetasInsumoFormSet(
                instance=self.object,  # ¡Esto es crucial!
                prefix='insumos'
            )            
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            response = super().form_valid(form)
            formset.instance = self.object
            formset.save()
            return response
        else:
            return self.form_invalid(form)

class EliminarRecetaView(DeleteView):
    model = Receta
    template_name = 'eliminar_receta.html'
    success_url = reverse_lazy('lista_receta')
    pk_url_kwarg = 'receta_id'