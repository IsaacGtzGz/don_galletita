from django.contrib import admin
from django.urls import path
from usuarios_app.views import ListaUsuariosView, CrearUsuarioView, LoginView

urlpatterns = [
    path('lista_usuarios/', ListaUsuariosView.as_view(), name='lista_usuarios'),
    path('crear_usuario/', CrearUsuarioView.as_view(), name='crear_usuario'),
    path('login_usuario/', LoginView.as_view(), name='login_usuario'),
]
