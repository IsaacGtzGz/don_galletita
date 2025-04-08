from django.urls import path
from . import views

urlpatterns = [
    path('compras/', views.ListaComprasView.as_view(), name='lista_compras'),
    path('compras/nueva/', views.CrearCompraView, name='crear_compra'),
    path('compras/<int:compra_id>/detalles/', views.VerDetallesView, name='ver_detalles'),
]