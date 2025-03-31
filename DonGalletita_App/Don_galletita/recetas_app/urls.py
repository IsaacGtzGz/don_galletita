from django.urls import path
from recetas_app.views import ListaRecetaView, CrearRecetaView, EditarRecetaView ,EliminarRecetaView

urlpatterns = [
    path('lista_recetas/', ListaRecetaView.as_view(), name='lista_receta'),
    path('crear_receta/', CrearRecetaView.as_view(), name='crear_receta'),
    path('editar_receta/<int:receta_id>/', EditarRecetaView.as_view(), name='editar_receta'),
    path('eliminar/<int:receta_id>/', EliminarRecetaView.as_view(), name='eliminar_receta'),
]