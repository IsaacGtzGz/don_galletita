from django.urls import path
from insumos_app.views import ListaInsumoView, CrearInsumoView, EditarInsumoView

urlpatterns = [
    path('listar_insumos/', ListaInsumoView.as_view(), name='lista_insumo'),
    path('crear_insumo/', CrearInsumoView.as_view(), name='crear_insumo'),
    path('editar_insumo/<int:insumo_id>/', EditarInsumoView.as_view(), name='editar_insumo'),
]
