from django.urls import path
from .views import ListaProductosView, CrearProductoView, EditarProductoView, EliminarProductoView, obtener_precio_producto

urlpatterns = [
    path('lista_productos/', ListaProductosView.as_view(), name='lista_productos'),
    path('crear_producto/', CrearProductoView.as_view(), name='crear_producto'),
    path('editar/<int:producto_id>/', EditarProductoView.as_view(), name='editar_producto'),
    path('eliminar/<int:producto_id>/', EliminarProductoView.as_view(), name='eliminar_producto'),
    path('obtener_precio_producto/<int:producto_id>/', obtener_precio_producto, name='obtener_precio_producto'),
]
