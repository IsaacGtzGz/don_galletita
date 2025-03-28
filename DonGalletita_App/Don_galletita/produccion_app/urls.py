"""
from django.urls import path
from . import views
from produccion_app.views import iniciar_produccion, listar_producciones, finalizar_produccion, gestion_recetas

app_name = 'productos'

urlpatterns = [
    path('produccion/iniciar/', views.iniciar_produccion, name='iniciar_produccion'),
    path('produccion/listar/', views.listar_producciones, name='listar_producciones'),
    path('produccion/finalizar/<int:produccion_id>/', views.finalizar_produccion, name='finalizar_produccion'),
    path('recetas/gestion/<int:producto_id>/', views.gestion_recetas, name='gestion_recetas'),
]"""