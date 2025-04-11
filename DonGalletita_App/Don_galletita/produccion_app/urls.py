from django.urls import path
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from produccion_app.views import (
    ListaProduccionView, CrearProduccionView, DetalleProduccionView, EliminarProduccionView, InventarioLotesView, RegistrarMermaView
)

urlpatterns = [
    path('listar/', login_required(ListaProduccionView.as_view()), name='lista_produccion'),
    path('invetario_lotes', login_required(InventarioLotesView.as_view()), name='inventario_lotes'),
    path('crear/', login_required(CrearProduccionView.as_view()), name='crear_produccion'),
    path('<int:pk>/', login_required(DetalleProduccionView.as_view()), name='detalle_produccion'),
    path('eliminar_produccion/<int:pk>/', login_required(EliminarProduccionView.as_view()), name='eliminar_produccion'),
    path('registrar-merma/<int:pk>/', RegistrarMermaView.as_view(), name='registrar_merma'),
]
