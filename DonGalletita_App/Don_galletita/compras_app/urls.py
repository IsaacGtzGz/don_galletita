from django.urls import path
from compras_app.views import ListaComprasView, CrearCompraView, EditarCompraView

urlpatterns = [
    path('lista_compras/', ListaComprasView.as_view(), name='lista_compras'),
    path('crear_compra/', CrearCompraView.as_view(), name='crear_compra'),
    path('editar_compra/<int:id>/', EditarCompraView.as_view(), name='editar_compra'),
]
