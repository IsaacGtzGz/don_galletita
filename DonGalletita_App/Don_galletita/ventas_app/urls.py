from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    ListaVentasView, CrearVentaView, EditarVentaView, EliminarVentaView,
    CrearDetalleVentaView, EditarDetalleVentaView, EliminarDetalleVentaView,
    CorteVentasDiarioView, TicketVentaView, DetalleVentaView,
    ExportarReportePDFView, ExportarReporteExcelView, ConfirmarVentaView,
    DashboardPresentacionesAlertasView, DashboardMetricasVentasView
)

urlpatterns = [
    # URL para crear, editar y eliminar ventas
    path('lista_ventas/', login_required(ListaVentasView.as_view()), name='lista_ventas'),
    path('crear_venta/', login_required(CrearVentaView.as_view()), name='crear_venta'),
    path('editar_venta/<int:id>/', login_required(EditarVentaView.as_view()), name='editar_venta'),
    path('eliminar_venta/<int:id>/', login_required(EliminarVentaView.as_view()), name='eliminar_venta'),

    # URL para crear, editar y eliminar detalles de venta
    path('crear_detalle_venta/<int:venta_id>/', login_required(CrearDetalleVentaView.as_view()), name='crear_detalle_venta'),
    path('editar_detalle_venta/<int:id>/', login_required(EditarDetalleVentaView.as_view()), name='editar_detalle_venta'),
    path('eliminar_detalle_venta/<int:id>/', login_required(EliminarDetalleVentaView.as_view()), name='eliminar_detalle_venta'),
    path('corte_ventas_diario/', login_required(CorteVentasDiarioView.as_view()), name='corte_ventas_diario'),
    path('ventas/ticket/<int:venta_id>/', login_required(TicketVentaView.as_view()), name='descargar_ticket'),
    path('detalle_venta/<int:venta_id>/', login_required(DetalleVentaView.as_view()), name='detalle_venta'),

    # URL para exportar reportes
    path('exportar_reporte_pdf/', login_required(ExportarReportePDFView.as_view()), name='exportar_reporte_pdf'),
    path('exportar_reporte_excel/', login_required(ExportarReporteExcelView.as_view()), name='exportar_reporte_excel'),

    # URL para confirmar ventas
    path('confirmar_venta/<int:venta_id>/', login_required(ConfirmarVentaView.as_view()), name='confirmar_venta'),

    # Dashboard
    path('dashboard/', login_required(DashboardPresentacionesAlertasView.as_view()), name='dashboard_presentaciones_alertas'),
    path('dashboard_metricas/', login_required(DashboardMetricasVentasView.as_view()), name='dashboard_metricas_ventas'),
]
