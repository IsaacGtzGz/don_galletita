from django.urls import path
from django.contrib.auth.decorators import login_required
from insumos_app.views import ListaInsumoView, CrearInsumoView, EditarInsumoView, EliminarInsumoView

urlpatterns = [
    path('lista_insumos/', login_required(ListaInsumoView.as_view()), name='lista_insumo'),
    path('crear_insumo/', login_required(CrearInsumoView.as_view()), name='crear_insumo'),
    path('editar_insumo/<int:insumo_id>/', login_required(EditarInsumoView.as_view()), name='editar_insumo'),
    path('eliminar/<int:insumo_id>/', login_required(EliminarInsumoView.as_view()), name='eliminar_insumo'),
]
