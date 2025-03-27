from django.urls import path
from proveedores_app.views import ListaProveedoresView, CrearProveedorView, EditarProveedorView

urlpatterns = [
    path('lista_proveedores/', ListaProveedoresView.as_view(), name='lista_proveedores'),
    path('crear_proveedor/', CrearProveedorView.as_view(), name='crear_proveedor'),
    path('editar_proveedor/<int:id>/', EditarProveedorView.as_view(), name='editar_proveedor'),
]
