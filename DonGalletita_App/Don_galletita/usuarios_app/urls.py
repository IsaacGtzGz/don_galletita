from django.contrib import admin
from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import lista_usuarios, editar_usuario, eliminar_usuario, registrar_usuario

urlpatterns = [
    path('usuarios/', login_required(lista_usuarios), name='lista_usuarios'),
    path('editar/<int:usuario_id>/', login_required(editar_usuario), name='editar_usuario'),
    path('eliminar/<int:usuario_id>/', login_required(eliminar_usuario), name='eliminar_usuario'),
    path('registrar/', login_required(registrar_usuario), name='registrar_usuario'),
    path('login/', views.login_personalizado, name='login'),
    path('logout/', views.logout_personalizado, name='logout'),
    path('registro/', views.registro_desde_login, name='registro'),
    path('completar_registro/<int:usuario_id>/', login_required(views.completar_registro), name='completar_registro'),
]