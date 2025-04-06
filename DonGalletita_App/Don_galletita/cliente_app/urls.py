from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('clientes/', login_required(views.lista_clientes), name='lista_clientes'),
    path('clientes/nuevo/', login_required(views.crear_cliente), name='crear_cliente'),
    path('clientes/<int:cliente_id>/', login_required(views.detalle_cliente), name='detalle_cliente'),
    path('clientes/<int:cliente_id>/editar/', login_required(views.editar_cliente), name='editar_cliente'),
    path('clientes/<int:cliente_id>/eliminar/', login_required(views.eliminar_cliente), name='eliminar_cliente'),
    path('carrito/carrito/', login_required(views.ver_carrito), name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', login_required(views.agregar_al_carrito), name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', login_required(views.eliminar_del_carrito), name='eliminar_del_carrito'),
    path('carrito/actualizar/<int:item_id>/', login_required(views.actualizar_carrito), name='actualizar_carrito'),
    path('carrito/limpiar/', login_required(views.limpiar_carrito), name='limpiar_carrito'),
    path('carrito/catalogo/', views.catalogo, name='catalogo'),  # Catalogo can be public

    # Portal del cliente
    path('portal/registro/', views.registro_cliente, name='registro_cliente'),  # Registration can be public
    path('portal/perfil/', login_required(views.perfil_cliente), name='perfil_cliente'),

    path('carrito/confirmar/', login_required(views.confirmar_compra), name='confirmar_compra'),
    path('carrito/ticket/<int:venta_id>/', login_required(views.generar_ticket), name='generar_ticket'),
    path('carrito/historial/', login_required(views.historial_compras), name='historial_compras'),
]
