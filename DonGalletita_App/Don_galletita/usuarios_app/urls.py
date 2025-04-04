from django.contrib import admin
from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('usuarios/', login_required(views.lista_usuarios), name='lista_usuarios'),
    path('usuarios/editar/<int:usuario_id>/', login_required(views.editar_usuario), name='editar_usuario'),
    path('usuarios/eliminar/<int:usuario_id>/', login_required(views.eliminar_usuario), name='eliminar_usuario'),
    path('login/', views.login_personalizado, name='login'),
    path('logout/', views.logout_personalizado, name='logout'),
    path('registro/', views.registro_desde_login, name='registro'),
    path('completar_registro/<int:usuario_id>/', login_required(views.completar_registro), name='completar_registro'),
]