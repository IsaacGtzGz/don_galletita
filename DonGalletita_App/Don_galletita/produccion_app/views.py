from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from .models import Produccion, LoteProduccion, ConsumoInsumos
from .forms import ProduccionForm, LoteProduccionForm
from recetas_app.models import Receta
from insumos_app.models import Insumos

class ListaProduccionView(ListView):
    model = Produccion
    template_name = 'lista_produccion.html'
    context_object_name = 'producciones'

class CrearProduccionView(CreateView):
    model = Produccion
    form_class = ProduccionForm
    template_name = 'crear_produccion.html'
    success_url = reverse_lazy('lista_produccion')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                produccion = form.save(commit=False)
                producto = produccion.producto
                cantidad = form.cleaned_data['cantidad_producida']
                
                # Verificar insumos
                recetas = Receta.objects.filter(producto=producto)
                for receta in recetas:
                    if receta.insumo.cantidad_disponible < (receta.cantidad_necesaria * cantidad):
                        raise ValueError(f"Insumo insuficiente: {receta.insumo.nombre_insumo}")
                
                # Guardar producción
                produccion.cantidad_producida = cantidad
                produccion.save()
                
                # Crear lote de producción
                lote = LoteProduccion.objects.create(
                    produccion=produccion,
                    cantidad_galletas=cantidad,
                    fecha_caducidad=form.cleaned_data['fecha_finalizacion'].date() if form.cleaned_data['fecha_finalizacion'] else None
                )
                
                # Actualizar inventario de insumos
                for receta in recetas:
                    ConsumoInsumos.objects.create(
                        produccion=produccion,
                        insumo=receta.insumo,
                        cantidad_usada=receta.cantidad_necesaria * cantidad
                    )
                    receta.insumo.cantidad_disponible -= receta.cantidad_necesaria * cantidad
                    receta.insumo.save()
                
                # Actualizar inventario de producto
                producto.cantidad_disponible += cantidad
                producto.save()
                
                messages.success(self.request, "Producción registrada exitosamente!")
                return super().form_valid(form)
                
        except Exception as e:
            messages.error(self.request, f"Error: {str(e)}")
            return self.form_invalid(form)

class DetalleProduccionView(DetailView):
    model = Produccion
    template_name = 'detalle_produccion.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lotes'] = LoteProduccion.objects.filter(produccion=self.object)
        context['consumos'] = ConsumoInsumos.objects.filter(produccion=self.object)
        return context

class EliminarProduccionView(DeleteView):
    model = Produccion
    template_name = 'confirmar_eliminar.html'
    success_url = reverse_lazy('lista_produccion')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Producción eliminada correctamente")
        return super().delete(request, *args, **kwargs)