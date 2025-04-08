from django.urls import path
from . import views

urlpatterns = [
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/nuevo/', views.crear_cliente, name='crear_cliente'),
    path('clientes/<int:cliente_id>/', views.detalle_cliente, name='detalle_cliente'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('clientes/<int:cliente_id>/eliminar/', views.eliminar_cliente, name='eliminar_cliente'),
    
    
    path('carrito/carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),  # Eliminar un producto
    path('carrito/actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),  # Modificar cantidad
    path('carrito/limpiar/', views.limpiar_carrito, name='limpiar_carrito'), 
    path('carrito/historial/', views.historial_compras, name='historial_compras'),
    path('carrito/catalogo/', views.catalogo, name='catalogo'),
    path('carrito/confirmar/', views.confirmar_compra, name='confirmar_compra'),
    

    # Portal del cliente
    path('portal/registro/', views.registro_cliente, name='registro_cliente'),
    path('portal/perfil/', views.perfil_cliente, name='perfil_cliente'),
    
]