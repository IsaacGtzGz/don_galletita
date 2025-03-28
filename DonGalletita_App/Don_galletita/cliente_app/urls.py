from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_clientes, name='lista_clientes'),
    path('nuevo/', views.crear_cliente, name='crear_cliente'),
    path('<int:id>/', views.detalle_cliente, name='detalle_cliente'),
    path('<int:id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('<int:id>/eliminar/', views.eliminar_cliente, name='eliminar_cliente'),
]