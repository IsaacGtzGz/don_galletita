from django.urls import path
from produccion_app.views import (ListaProduccionView, CrearProduccionView, DetalleProduccionView, EliminarProduccionView
)

urlpatterns = [
    path('listar/', ListaProduccionView.as_view(), name='lista_produccion'),
    path('crear/', CrearProduccionView.as_view(), name='crear_produccion'),
    path('<int:pk>/', DetalleProduccionView.as_view(), name='detalle_produccion'),
    path('eliminar/<int:pk>/', EliminarProduccionView.as_view(), name='eliminar_produccion'),
]
