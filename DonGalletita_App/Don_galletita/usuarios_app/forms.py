from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from usuarios_app.models import Usuario

class UsuarioForm(UserCreationForm):
    nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    apellido_paterno = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido Paterno'
        })
    )
    apellido_materno = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido Materno'
        })
    )
    telefono = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono'
        }),
        validators=[
            MinLengthValidator(10),
            RegexValidator(
                regex='^[0-9]+$',
                message='Solo números permitidos'
            )
        ]
    )
    direccion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Dirección'
        }),
        required=True
    )
    rol = forms.ChoiceField(
        choices=[('admin', 'Administrador'), ('empleado', 'Empleado')],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=True
    )

    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'password1', 'password2', 'email']
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de Usuario'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo Electrónico'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar los mensajes de ayuda predeterminados para las contraseñas
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.rol = self.cleaned_data['rol']
        if commit:
            usuario.save()
        return usuario

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Las contraseñas no coinciden.")

            try:
                password_validation.validate_password(password2, self.instance)
            except ValidationError as e:
                self.add_error('password2', e.messages)

        return password2


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
    nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    apellido_paterno = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido Paterno'
        })
    )
    apellido_materno = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido Materno'
        })
    )
    telefono = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono'
        })
    )
    direccion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Dirección'
        }),
        required=True
    )
    rol = forms.ChoiceField(
        choices=[('admin', 'Administrador'), ('empleado', 'Empleado')],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=True
    )

    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'email', 'rol', 'is_active']
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de Usuario'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo Electrónico'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
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