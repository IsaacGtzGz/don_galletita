from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from .forms import CompraRegistrarForm, DetalleCompraFormSet
from .models import Compra
from django.views.generic import TemplateView

# Listar compras
class ListaComprasView(TemplateView):
    template_name = 'lista_compras.html'

    def get_context_data(self):
        lista = Compra.objects.all()
        return {'lista': lista}

# Crear una compra
def CrearCompraView(request):
    if request.method == 'POST':
        compra_form = CompraRegistrarForm(request.POST)
        detalle_formset = DetalleCompraFormSet(request.POST, prefix='detalle_formset')

        if compra_form.is_valid() and detalle_formset.is_valid():
            # Guardar la compra
            compra = compra_form.save()

            # Guardar los detalles de la compra
            detalles = detalle_formset.save(commit=False)
            for detalle in detalles:
                detalle.compra = compra
                detalle.save()

            return redirect(reverse_lazy('lista_compras'))

        # Si hay errores, renderizar la página con los errores
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