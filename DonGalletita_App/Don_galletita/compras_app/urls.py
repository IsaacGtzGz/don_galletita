from django.urls import path
from . import views

urlpatterns = [
    # Ruta para crear una nueva compra
    path('crear_compra/', views.CrearCompraView.as_view(), name='crear_compra'),

    # Ruta para listar todas las compras
    path('listar_compras/', views.ListaComprasView.as_view(), name='listar_compras'),

    # Ruta para listar productos de materia prima
    path('listar_productos_materia_prima/', views.ListaProductosMateriaPrimaView.as_view(), name='listar_productos_materia_prima'),

    # Ruta para ver los detalles de una compra específica
    path('ver_detalles_compra/<int:id>/', views.VerDetallesCompraView.as_view(), name='ver_detalles_compra'),

    # Ruta para eliminar una compra (si es necesario)
    path('eliminar_compra/<int:id>/', views.EliminarCompraView.as_view(), name='eliminar_compra'),
]
