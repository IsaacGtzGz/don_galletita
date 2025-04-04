from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('compras/', login_required(views.ListaComprasView.as_view()), name='lista_compras'),
    path('compras/nueva/', login_required(views.CrearCompraView), name='crear_compra'),
    path('compras/<int:compra_id>/detalles/', login_required(views.VerDetallesView), name='ver_detalles'),
]