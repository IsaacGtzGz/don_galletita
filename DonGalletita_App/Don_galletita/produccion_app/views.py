from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from .models import Produccion, LoteProduccion, ConsumoInsumos
from .forms import ProduccionForm, LoteProduccionForm
from recetas_app.models import Receta, RecetaInsumo
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
                receta = Receta.objects.get(producto=producto)
                
                for receta_insumo in RecetaInsumo.objects.filter(receta=receta):
                    cantidad_necesaria = receta_insumo.cantidad_necesaria * cantidad
                    
                    # Conversión de unidades si es necesario
                    if receta_insumo.unidad_medida == 'g' and receta_insumo.insumo.unidad_medida == 'kg':
                        cantidad_necesaria /= 1000
                    elif receta_insumo.unidad_medida == 'kg' and receta_insumo.insumo.unidad_medida == 'g':
                        cantidad_necesaria *= 1000
                    # Agrega otras conversiones necesarias aquí
                    
                    if receta_insumo.insumo.cantidad_disponible < cantidad_necesaria:
                        raise ValueError(
                            f"Insumo insuficiente: {receta_insumo.insumo.nombre_insumo}\n"
                            f"Necesitas {cantidad_necesaria} {receta_insumo.insumo.unidad_medida} "
                            f"(tienes {receta_insumo.insumo.cantidad_disponible})"
                        )
                
                produccion.save()
                lote = LoteProduccion.objects.create(
                    produccion=produccion,
                    cantidad_galletas=cantidad,
                    fecha_caducidad=form.cleaned_data['fecha_finalizacion'].date() if form.cleaned_data['fecha_finalizacion'] else None
                )
                
                for receta_insumo in RecetaInsumo.objects.filter(receta=receta):
                    cantidad_usada = receta_insumo.cantidad_necesaria * cantidad
                    # Aplica misma conversión para el descuento
                    if receta_insumo.unidad_medida == 'g' and receta_insumo.insumo.unidad_medida == 'kg':
                        cantidad_usada /= 1000
                    elif receta_insumo.unidad_medida == 'kg' and receta_insumo.insumo.unidad_medida == 'g':
                        cantidad_usada *= 1000
                    
                    ConsumoInsumos.objects.create(
                        produccion=produccion,
                        insumo=receta_insumo.insumo,
                        cantidad_usada=cantidad_usada
                    )
                    receta_insumo.insumo.cantidad_disponible -= cantidad_usada
                    receta_insumo.insumo.save()
                
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
    template_name = 'eliminar_produccion.html'
    success_url = reverse_lazy('lista_produccion')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Producción eliminada correctamente")
        return super().delete(request, *args, **kwargs)
