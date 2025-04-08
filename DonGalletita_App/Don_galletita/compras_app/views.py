from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from .forms import CompraRegistrarForm, DetalleCompraFormSet
from .models import Compra
from insumos_app.models import Insumos
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime  # Importar datetime para manejar conversiones de fecha
from django.utils import timezone  # Importar timezone para manejar zonas horarias

logger = logging.getLogger(__name__)

# Listar compras
class ListaComprasView(LoginRequiredMixin, TemplateView):
    template_name = 'lista_compras.html'
    login_url = 'login'  # Redirige a la página de inicio de sesión si no está autenticado

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')  # Obtén el parámetro de búsqueda
        if query:
            try:
                # Convertir la cadena de fecha a un objeto de tipo datetime
                fecha = datetime.strptime(query, '%Y-%m-%d')
                # Hacer que el datetime sea "aware" con la zona horaria configurada
                fecha_aware = timezone.make_aware(fecha)
                # Filtrar las compras cuya fecha_compra coincide con la fecha ingresada
                context['lista'] = Compra.objects.filter(fecha_compra__date=fecha_aware.date())
            except ValueError:
                # Si la fecha no es válida, no se filtra nada
                context['lista'] = Compra.objects.none()
        else:
            # Muestra todas las compras si no hay búsqueda
            context['lista'] = Compra.objects.all()
        return context

# Crear una compra
@login_required
def CrearCompraView(request):
    if request.method == 'POST':
        compra_form = CompraRegistrarForm(request.POST)
        detalle_formset = DetalleCompraFormSet(request.POST, prefix='detalle_formset')

        if compra_form.is_valid() and detalle_formset.is_valid():
            compra = compra_form.save()
            detalles = detalle_formset.save(commit=False)
            for detalle in detalles:
                detalle.compra = compra
                detalle.save()
                insumo = detalle.insumo
                insumo.cantidad_disponible += detalle.cantidad
                insumo.save()

            logger.info(f"Compra creada por {request.user}: {compra}")
            return redirect(reverse_lazy('lista_compras'))

        return render(request, 'crear_compra.html', {
            'form': compra_form,
            'detalle_formset': detalle_formset
        })
    else:
        compra_form = CompraRegistrarForm()
        detalle_formset = DetalleCompraFormSet(prefix='detalle_formset')
        return render(request, 'crear_compra.html', {
            'form': compra_form,
            'detalle_formset': detalle_formset
        })

def VerDetallesView(request, compra_id):
    compra = get_object_or_404(Compra, compra_id=compra_id)
    return render(request, 'ver_detalles.html', {'compra': compra})

def obtener_unidad_medida(request):
    insumo_id = request.GET.get('insumo_id')
    if insumo_id:
        try:
            insumo = Insumos.objects.get(id=insumo_id)
            return JsonResponse({'unidad_medida': insumo.unidad_medida})
        except Insumos.DoesNotExist:
            return JsonResponse({'error': 'Insumo no encontrado'}, status=404)
    return JsonResponse({'error': 'ID de insumo no proporcionado'}, status=400)