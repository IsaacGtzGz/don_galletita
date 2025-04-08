from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from .models import Produccion, LoteProduccion, ConsumoInsumos
from .forms import ProduccionForm, LoteProduccionForm
from recetas_app.models import Receta, RecetaInsumo
from insumos_app.models import Insumos
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.utils.timezone import now, timedelta
from productos_app.models import Producto
from recetas_app.models import Receta
from .models import Produccion

class ListaProduccionView(ListView):
    model = Produccion
    template_name = 'lista_produccion.html'
    context_object_name = 'producciones'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')  # Obtén el parámetro de búsqueda
        if query:
            # Filtra las producciones cuyo nombre de receta contiene el texto ingresado
            context['producciones'] = Produccion.objects.filter(receta__producto__nombre__icontains=query)
        else:
            # Muestra todas las producciones si no hay búsqueda
            context['producciones'] = Produccion.objects.all()
        return context

# produccion_app/views.py
class CrearProduccionView(CreateView):
    model = Produccion
    form_class = ProduccionForm
    template_name = 'crear_produccion.html'
    success_url = reverse_lazy('lista_produccion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recetas'] = Receta.objects.filter(producto__isnull=False).select_related('producto')
        return context

    def form_valid(self, form):
        try:
            with transaction.atomic():
                # 1. Obtener datos del formulario
                receta_id = self.request.POST.get('receta_id')
                cantidad_galletas = int(self.request.POST.get('porciones_galletas', 0))
                fecha_finalizacion = form.cleaned_data['fecha_finalizacion']
                fecha_caducidad_str = self.request.POST.get('fecha_caducidad')
                
                # 2. Validar fecha de caducidad
                if not fecha_caducidad_str:
                    messages.error(self.request, "La fecha de caducidad es obligatoria")
                    return self.form_invalid(form)
                
                try:
                    fecha_caducidad = timezone.datetime.strptime(fecha_caducidad_str, '%Y-%m-%d').date()
                except ValueError:
                    messages.error(self.request, "Formato de fecha incorrecto. Use YYYY-MM-DD")
                    return self.form_invalid(form)

                # Validar que la fecha de caducidad sea posterior a la producción
                if fecha_caducidad <= fecha_finalizacion.date():
                    messages.error(self.request, "La fecha de caducidad debe ser posterior a la fecha de producción")
                    return self.form_invalid(form)

                # 3. Obtener receta y producto
                receta = get_object_or_404(Receta, pk=receta_id)
                producto = receta.producto
                
                # 4. Crear registro de producción
                produccion = Produccion(
                    receta=receta,
                    cantidad_producida=cantidad_galletas,
                    fecha_finalizacion=fecha_finalizacion
                )
                produccion.save()

                # 5. Validar y descontar insumos con merma implícita - CORRECCIÓN DE INDENTACIÓN
                for ri in receta.recetainsumo_set.all():
                    # Convertir a la unidad base del insumo
                    cantidad_necesaria = Decimal(str(ri.cantidad_necesaria))  # Cambio clave aquí
                    
                    if ri.unidad_medida == 'g' and ri.insumo.unidad_medida == 'kg':
                        cantidad_necesaria /= Decimal('1000')  # Usar Decimal para la división
                    elif ri.unidad_medida == 'kg' and ri.insumo.unidad_medida == 'g':
                        cantidad_necesaria *= Decimal('1000')  # Usar Decimal para la multiplicación
                    
                    # Calcular merma exacta
                    cantidad_total_usada = round(cantidad_necesaria * Decimal('1.05'), 3)  # Cambio clave aquí
                    
                    # Verificar disponibilidad (convertir a Decimal para comparación)
                    if Decimal(str(ri.insumo.cantidad_disponible)) < cantidad_total_usada:  # Cambio aquí
                        messages.error(self.request, 
                            f"Insumo insuficiente: {ri.insumo.nombre_insumo} "
                            f"(Necesitas {float(cantidad_total_usada):.3f} {ri.insumo.unidad_medida}, "
                            f"tienes {float(ri.insumo.cantidad_disponible):.3f} {ri.insumo.unidad_medida})"
                        )
                        return self.form_invalid(form)
                    
                    # Descontar exactamente con merma (usando Decimal)
                    ri.insumo.cantidad_disponible -= cantidad_total_usada  # Ahora sí compatible
                    ri.insumo.save()
                    
                    # Registrar en consumo (cantidad REAL sin merma)
                    ConsumoInsumos.objects.create(
                        produccion=produccion,
                        insumo=ri.insumo,
                        cantidad_usada=float(cantidad_necesaria)  # Guardar como float
                    )

                # 6. Actualizar producto terminado
                producto.cantidad_disponible += cantidad_galletas
                producto.save()

                # 7. Registrar lote de producción con fecha de caducidad específica
                lote = LoteProduccion.objects.create(
                    produccion=produccion,
                    cantidad_galletas=cantidad_galletas,
                    fecha_caducidad=fecha_caducidad,
                    estado='disponible'  # Puede ser: disponible, por_caducar, caducado
                )

                # 8. Verificar si el lote está próximo a caducar (2 días antes)
                if (fecha_caducidad - timezone.now().date()) <= timedelta(days=2):
                    lote.estado = 'por_caducar'
                    lote.save()
                    messages.warning(self.request, 
                        f"¡Atención! El lote {lote.lote_id} caduca pronto ({fecha_caducidad}). "
                        "Se moverá a merma automáticamente."
                    )

                messages.success(self.request, 
                    f"¡Producción registrada exitosamente! Lote: {lote.lote_id} "
                    f"(Caducidad: {fecha_caducidad})"
                )
                return redirect(self.success_url)
                
        except Exception as e:
            messages.error(self.request, f"Error al registrar la producción: {str(e)}")
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

def crear_produccion_automatica(producto_id, cantidad_necesaria):
    try:
        producto = Producto.objects.get(producto_id=producto_id)
        receta = Receta.objects.get(producto=producto)

        if not receta:
            raise ValueError("El producto no tiene una receta asociada.")

        # Crear un registro de producción
        fecha_finalizacion = now() + timedelta(days=1)  # Asumimos que la producción tarda 1 día
        fecha_caducidad = fecha_finalizacion + timedelta(days=30)  # Caducidad 30 días después

        produccion = Produccion.objects.create(
            receta=receta,
            cantidad_producida=cantidad_necesaria,
            fecha_finalizacion=fecha_finalizacion,
            fecha_caducidad=fecha_caducidad
        )

        # Actualizar el inventario del producto
        producto.cantidad_disponible += cantidad_necesaria
        producto.save()

        return produccion
    except Producto.DoesNotExist:
        raise ValueError("El producto especificado no existe.")
    except Exception as e:
        raise ValueError(f"Error al crear la producción automática: {str(e)}")