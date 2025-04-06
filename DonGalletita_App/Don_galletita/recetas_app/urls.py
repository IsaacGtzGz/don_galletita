from django.urls import path
from django.contrib.auth.decorators import login_required
from recetas_app.views import ListaRecetaView, CrearRecetaView, EditarRecetaView, EliminarRecetaView

urlpatterns = [
    path('lista_recetas/', login_required(ListaRecetaView.as_view()), name='lista_receta'),
    path('crear_receta/', login_required(CrearRecetaView.as_view()), name='crear_receta'),
    path('editar_receta/<int:receta_id>/', login_required(EditarRecetaView.as_view()), name='editar_receta'),
    path('eliminar/<int:receta_id>/', login_required(EliminarRecetaView.as_view()), name='eliminar_receta'),
]