from django.urls import path
from . import views

urlpatterns = [
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/nuevo/', views.crear_cliente, name='crear_cliente'),
    path('clientes/<int:cliente_id>/', views.detalle_cliente, name='detalle_cliente'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('clientes/<int:cliente_id>/eliminar/', views.eliminar_cliente, name='eliminar_cliente'),
    
    # Portal del cliente
    path('portal/registro/', views.registro_cliente, name='registro_cliente'),
    path('portal/perfil/', views.perfil_cliente, name='perfil_cliente'),
    path('portal/carrito/', views.carrito_compras, name='carrito_compras'),
    path('portal/carrito/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('portal/carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('portal/historial/', views.historial_compras, name='historial_compras'),
    path('portal/historial/cancelar/<int:venta_id>/', views.cancelar_pedido, name='cancelar_pedido'),
]