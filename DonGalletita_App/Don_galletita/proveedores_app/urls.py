from django.urls import path
from django.contrib.auth.decorators import login_required
from proveedores_app.views import ListaProveedoresView, CrearProveedorView, EditarProveedorView, EliminarProveedorView

urlpatterns = [
    path('lista_proveedores/', login_required(ListaProveedoresView.as_view()), name='lista_proveedores'),
    path('crear_proveedor/', login_required(CrearProveedorView.as_view()), name='crear_proveedor'),
    path('editar_proveedor/<int:id>/', login_required(EditarProveedorView.as_view()), name='editar_proveedor'),
    path('eliminar_proveedor/<int:id>/', login_required(EliminarProveedorView.as_view()), name='eliminar_proveedor'),
]
