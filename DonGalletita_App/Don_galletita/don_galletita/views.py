from django.shortcuts import render, redirect
from django.http import HttpResponse
<<<<<<< HEAD
from django.contrib.auth import login
=======
from usuarios_app.forms import UsuarioRegistrarForm
>>>>>>> origin/master
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from usuarios_app.models import Usuario
from django.contrib.auth import login

<<<<<<< HEAD
=======
# Eliminé cualquier referencia al login en las vistas.
>>>>>>> origin/master

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)
                  
def home(request):
    return render(request, 'home.html')

def index(request):
    return render(request, 'index.html')

def registro(request):
    if request.method == 'POST':
        nombre_usuario = request.POST.get('nombre_usuario')
        contrasenia = request.POST.get('contrasenia')
        rol = request.POST.get('rol', 'cliente')  # Valor predeterminado para el rol

        if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
        else:
            usuario = Usuario(
                nombre_usuario=nombre_usuario,
                rol=rol
            )
            usuario.set_password(contrasenia)  # Encriptar la contraseña
            usuario.save()
            login(request, usuario)  # Iniciar sesión automáticamente
            return render(request, 'usuarios/completar_registro.html', {'usuario': usuario})
    return render(request, 'registration/login.html')
