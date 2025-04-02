from django.urls import path
from .views import (
    ListaVentasView, CrearVentaView, EditarVentaView, EliminarVentaView,
    CrearDetalleVentaView, EditarDetalleVentaView, EliminarDetalleVentaView,
    CorteVentasDiarioView, TicketVentaView, DetalleVentaView
)

urlpatterns = [
    path('lista_ventas/', ListaVentasView.as_view(), name='lista_ventas'),
    path('crear_venta/', CrearVentaView.as_view(), name='crear_venta'),
    path('editar_venta/<int:id>/', EditarVentaView.as_view(), name='editar_venta'),
    path('eliminar_venta/<int:id>/', EliminarVentaView.as_view(), name='eliminar_venta'),

    path('crear_detalle_venta/<int:venta_id>/', CrearDetalleVentaView.as_view(), name='crear_detalle_venta'),
    path('editar_detalle_venta/<int:id>/', EditarDetalleVentaView.as_view(), name='editar_detalle_venta'),
    path('eliminar_detalle_venta/<int:id>/', EliminarDetalleVentaView.as_view(), name='eliminar_detalle_venta'),
    path('corte_ventas_diario/', CorteVentasDiarioView.as_view(), name='corte_ventas_diario'),
    path('ventas/ticket/<int:venta_id>/', TicketVentaView.as_view(), name='descargar_ticket'),
    path('detalle_venta/<int:venta_id>/', DetalleVentaView.as_view(), name='detalle_venta'),
]
