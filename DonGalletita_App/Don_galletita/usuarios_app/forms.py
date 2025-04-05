from django import forms
from . import models
class UsuarioRegistrarForm(forms.ModelForm):
    class Meta:
        model = models.Usuario
        fields = ['nombre_usuario', 'contrasenia', 'rol', 'estatus_user']
        widgets = {
            "nombre_usuario": forms.TextInput(attrs={"class": "form-control"}),
            "contrasenia": forms.PasswordInput(attrs={"class": "form-control"}),
            "rol": forms.Select(attrs={"class": "form-control"}),
            "estatus_user": forms.NumberInput(attrs={"class": "form-control"})
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        if commit:
            usuario.save()
        return usuario


class UsuarioEditarForm(forms.ModelForm):
    class Meta:
        model = models.Usuario
        fields = ['nombre_usuario', 'contrasenia', 'rol', 'estatus_user']
        widgets = {
            "nombre_usuario": forms.TextInput(attrs={"class": "form-control"}),
            "contrasenia": forms.PasswordInput(attrs={"class": "form-control"}),
            "rol": forms.Select(attrs={"class": "form-control"}),
            "estatus_user": forms.NumberInput(attrs={"class": "form-control"})
        }

    def save(self, id, commit=True):
        usuario = models.Usuario.objects.filter(usuario_id=id).first()
        usuario.nombre_usuario = self.cleaned_data["nombre_usuario"]
        usuario.set_password(self.cleaned_data["contrasenia"])
        usuario.rol = self.cleaned_data["rol"]
        usuario.estatus_user = self.cleaned_data["estatus_user"]
        if commit:
            usuario.save()
        return usuario