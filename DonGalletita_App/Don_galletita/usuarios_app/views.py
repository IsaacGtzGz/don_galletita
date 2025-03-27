from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.db import connection
from .forms import UsuarioRegistrarForm, UsuarioEditarForm
from .models import Usuario

# CRUD para usuarios
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})

def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == 'POST':
        form = UsuarioEditarForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save(id=usuario_id)  # Pasamos el ID del usuario al método save
            return redirect('lista_usuarios')
    else:
        form = UsuarioEditarForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form})

def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        return redirect('lista_usuarios')
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})

def login_personalizado(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Intentar autenticar al usuario usando el ORM de Django
        usuario = Usuario.objects.filter(nombre_usuario=username).first()

        # Mostrar mensaje de error si el usuario no existe o la contraseña es incorrecta
        if not usuario:
            messages.error(request, "El usuario no está registrado. Por favor, complete el formulario de registro.")
            return render(request, 'registration/login.html', {"show_register_form": True, "messages": messages.get_messages(request)})
        elif not usuario.check_password(password):
            messages.error(request, "Contraseña incorrecta.")
        else:
            login(request, usuario)
            return redirect('home')

    return render(request, 'registration/login.html')

def logout_personalizado(request):
    request.session.flush()
    return redirect('login')

def registro_desde_login(request):
    if request.method == 'POST':
        nombre_usuario = request.POST.get('nombre_usuario')
        contrasenia = request.POST.get('contrasenia')

        if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
            messages.error(request, "El nombre de usuario ya está registrado.")
        else:
            usuario = Usuario(
                nombre_usuario=nombre_usuario,
                rol='cliente',  # Rol por defecto
                estatus_user=1
            )
            usuario.set_password(contrasenia)  # Encripta la contraseña
            usuario.save()
            messages.success(request, "Usuario registrado exitosamente.")
            return redirect('completar_registro', usuario_id=usuario.usuario_id)

    return render(request, 'registration/login.html')

def completar_registro(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    return render(request, 'usuarios/completar_registro.html', {'usuario': usuario})
