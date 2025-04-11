from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.db import connection
from .forms import UsuarioRegistrarForm, UsuarioEditarForm, UsuarioForm
from .models import Usuario
from django.contrib.auth.models import Group  # Importar el modelo Group
import logging
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.html import escape

# Configuración del logger
logger = logging.getLogger('usuarios_app')

# Verificar si el usuario es administrador
def es_admin(user):
    return user.is_authenticated and user.rol == 'admin'

@login_required
@user_passes_test(es_admin)
def registrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario registrado exitosamente.')
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'registrar_usuario.html', {'form': form})

# CRUD para usuarios
def lista_usuarios(request):
    query = escape(request.GET.get('q', ''))  # Obtén el parámetro de búsqueda y escápalo
    if query:
        # Filtra los usuarios cuyo nombre de usuario contiene el texto ingresado
        usuarios = Usuario.objects.filter(nombre_usuario__icontains=query)
    else:
        # Muestra todos los usuarios si no hay búsqueda
        usuarios = Usuario.objects.all()
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})

def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            if form.cleaned_data['password1']:
                usuario.set_password(form.cleaned_data['password1'])  # Actualizar contraseña si se proporciona
            usuario.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('lista_usuarios')
    else:
        # Cargar datos existentes del usuario en el formulario
        form = UsuarioForm(instance=usuario, initial={
            'nombre_usuario': usuario.nombre_usuario,
            'email': usuario.email,
            'telefono': getattr(usuario, 'telefono', ''),
            'direccion': getattr(usuario, 'direccion', ''),
            'nombre': getattr(usuario, 'nombre', ''),
            'apellido_paterno': getattr(usuario, 'apellido_paterno', ''),
            'apellido_materno': getattr(usuario, 'apellido_materno', ''),
        })
    return render(request, 'editar_usuario.html', {'form': form, 'usuario': usuario})

def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        return redirect('lista_usuarios')
    return render(request, 'eliminar_usuario.html', {'usuario': usuario})

def login_personalizado(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        contrasenia = request.POST.get('contrasenia')

        # Intentar autenticar al usuario usando el ORM de Django
        usuario = Usuario.objects.filter(nombre_usuario=username).first()

        # Redirigir al formulario de registro si el usuario no está registrado
        if not usuario:
            messages.error(request, "El usuario no está registrado. Por favor, complete el formulario de registro.")
            return redirect('registro')
        elif not usuario.check_password(contrasenia):
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
            try:
                usuario = Usuario(
                    nombre_usuario=nombre_usuario,
                    rol='Cliente',  # Rol por defecto
                    estatus_user=1
                )
                usuario.set_password(contrasenia)  # Encripta la contraseña
                usuario.save()

                # Asignar el usuario al grupo "Cliente"
                grupo, created = Group.objects.get_or_create(name="Cliente")
                usuario.groups.add(grupo)

                # Registrar el evento en el log
                logger.info(f"Nuevo usuario registrado: {usuario.nombre_usuario} el {now()}")

                messages.success(request, "Usuario registrado exitosamente.")
                return redirect('portal/registro_cliente', usuario_id=usuario.usuario_id)
            except Exception as e:
                # Captura cualquier error inesperado
                logger.error(f"Error inesperado en el registro de usuario: {e} - {now()}")
                messages.error(request, "Ocurrió un error al registrar el usuario.")

    return render(request, 'registration/login.html')

def completar_registro(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    return render(request, 'usuarios/completar_registro.html', {'usuario': usuario})
