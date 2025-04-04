from django.urls import path
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .views import ListaProductosView, CrearProductoView, EditarProductoView, EliminarProductoView, obtener_precio_producto

urlpatterns = [
    path('lista_productos/', login_required(ListaProductosView.as_view()), name='lista_productos'),
    path('crear_producto/', login_required(CrearProductoView.as_view()), name='crear_producto'),
    path('editar/<int:producto_id>/', login_required(EditarProductoView.as_view()), name='editar_producto'),
    path('eliminar/<int:producto_id>/', login_required(EliminarProductoView.as_view()), name='eliminar_producto'),
    path('obtener_precio_producto/<int:producto_id>/', login_required(obtener_precio_producto), name='obtener_precio_producto'),
]
