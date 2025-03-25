from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login
from usuarios_app.models import Usuario
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from . import forms
from django.urls import reverse_lazy
from django.contrib import messages

# Create your views here.
class ListaUsuariosView(TemplateView):
    template_name = 'lista_usuarios.html'

    def get_context_data(self):
        lista = Usuario.objects.all()
        return {'lista': lista}
    
# Crear un usuario
class CrearUsuarioView(FormView):
    template_name = 'crear_usuario.html'  
    form_class = forms.UsuarioRegistrarForm
    success_url = reverse_lazy('lista_usuarios')
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
class LoginView(TemplateView):
    template_name = "login_usuario.html"  # Reemplaza con el nombre correcto de tu HTML

    def post(self, request, *args, **kwargs):
        nombre_usuario = request.POST.get("username")
        contrasenia = request.POST.get("password")

        try:
            usuario = Usuario.objects.get(nombre_usuario=nombre_usuario, contrasenia=contrasenia)
            request.session["usuario_id"] = usuario.usuario_id  # Guardar sesión manualmente
            return redirect("lista_usuarios")  # Redirige a la página de inicio o dashboard
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario o contraseña incorrectos.")
        
        return render(request, self.template_name)