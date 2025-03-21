from django.shortcuts import get_object_or_404, redirect
from usuarios_app.models import Usuario
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from . import forms
from django.urls import reverse_lazy

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
        form.save(user=self.request.user)
        return super().form_valid(form)
    
# Editar un usuario    
class EditarUsuarioView(FormView):
    template_name = 'editar_usuario.html'  
    form_class = forms.UsuarioEditarForm
    success_url = reverse_lazy('lista_usuarios')
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        id = self.kwargs.get('id')
        usuario = get_object_or_404(Usuario, id=id)
        kwargs['instance'] = usuario
        return kwargs
    
    def form_valid(self, form):
        form.save(self.kwargs.get('id'), user=self.request.user)    
        return super().form_valid(form)
