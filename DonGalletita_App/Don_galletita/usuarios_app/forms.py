from django import forms
from . import models
class UsuarioRegistrarForm(forms.ModelForm):
    class Meta:
        model = models.Usuario
        fields = ['nombre_usuario', 'contrasenia', 'rol', 'estatus_user']
        widgets = {
            "nombre_usuario": forms.TextInput(attrs={
                "class": "input",
                "placeholder": "User name"
            }),
            "contrasenia": forms.PasswordInput(attrs={
                "class": "input",
                "placeholder": "Password"
            }),
            "rol": forms.Select(attrs={
                "class": "input",
                "style": "display: block; width: 60%; padding: 12px; margin: 20px auto; border: none; outline: none; border-radius: 5px; background: #e0dede;"
            }),
            "estatus_user": forms.HiddenInput()
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.contrasenia = self.cleaned_data["contrasenia"]

        if commit:
            usuario.save()
        return usuario
