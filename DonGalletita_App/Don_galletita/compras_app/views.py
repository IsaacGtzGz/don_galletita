from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.timezone import now
from django.views import View
from .models import Compra, DetalleCompra, ProductoAlmacenado
from .forms import CompraForm, DetalleCompraForm

class ListaComprasView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        compras = Compra.objects.filter(
            Q(proveedor__nombre__icontains=query) | Q(compra_id__icontains=query)
        ).order_by('-fecha_compra')
        paginator = Paginator(compras, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'compras/listar_compras.html', {'page_obj': page_obj, 'query': query})


class VerDetallesCompraView(View):
    def get(self, request, id):
        compra = get_object_or_404(Compra, pk=id)
        detalles = compra.detallecompra_set.all()
        for detalle in detalles:
            detalle.caducidad_proxima = detalle.fecha_caducidad and (detalle.fecha_caducidad - now().date()).days <= 5
        total = sum(detalle.cantidad * detalle.precio for detalle in detalles)
        return render(request, 'compras/ver_detalle_compras.html', {
            'compra': compra,
            'detalles': detalles,
            'total': total,
        })


class CrearCompraView(View):
    def get(self, request):
        form = CompraForm()
        detalle_form = DetalleCompraForm()
        return render(request, 'compras/crear_compra.html', {
            'form': form,
            'detalle_form': detalle_form,
        })

    def post(self, request):
        form = CompraForm(request.POST)
        if form.is_valid():
            compra = form.save()
            detalles = request.POST.getlist('detalles')
            for detalle_data in detalles:
                detalle_form = DetalleCompraForm(detalle_data)
                if detalle_form.is_valid():
                    detalle = detalle_form.save(commit=False)
                    detalle.compra = compra
                    detalle.save()
            return redirect('listar_compras')
        return render(request, 'compras/crear_compra.html', {'form': form})


class ListaProductosMateriaPrimaView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        productos = ProductoAlmacenado.objects.all()

        if query:
            productos = productos.filter(insumo__nombre__icontains=query)
        if fecha_inicio and fecha_fin:
            productos = productos.filter(fecha_caducidad__range=[fecha_inicio, fecha_fin])

        paginator = Paginator(productos, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'compras/listar_productos_materia_prima.html', {'page_obj': page_obj})