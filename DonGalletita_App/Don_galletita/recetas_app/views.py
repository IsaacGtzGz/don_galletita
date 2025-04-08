from django.shortcuts import render, get_object_or_404
from recetas_app.models import Receta, RecetaInsumo
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
    template_name = 'editar_receta.html'
    form_class = forms.RecetaEditarForm
    success_url = reverse_lazy('lista_receta')  # 🔹 Redirigir correctamente después de guardar

    def get_object(self, queryset=None):
        return get_object_or_404(Receta, receta_id=self.kwargs.get('receta_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = forms.RecetasInsumoFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix='insumos'
            )
        else:
            context['formset'] = forms.RecetasInsumoFormSet(
                instance=self.object,
                prefix='insumos'
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            
            # Guardar primero los objetos no marcados para borrar
            instances = formset.save(commit=False)
            for instance in instances:
                instance.receta = self.object
                instance.save()
            
            # Eliminar los objetos marcados para borrar
            for obj in formset.deleted_objects:
                obj.delete()
            
            return super().form_valid(form)
        else:
            print("Errores en el formset:", formset.errors)
            return self.render_to_response(self.get_context_data(form=form))
            

class EliminarRecetaView(DeleteView):
    model = Receta
    template_name = 'eliminar_receta.html'
    success_url = reverse_lazy('lista_receta')
    pk_url_kwarg = 'receta_id'