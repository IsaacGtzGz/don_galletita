from django.urls import path
from . import views
from produccion_app.views import iniciar_produccion, finalizar_produccion

urlpatterns = [
    path('produccion/iniciar/', views.iniciar_produccion, name='iniciar_produccion'),
    path('produccion/finalizar/<int:produccion_id>/', views.finalizar_produccion, name='finalizar_produccion'),
    #path('recetas/gestion/<int:producto_id>/', views.gestion_recetas, name='gestion_recetas'),
]