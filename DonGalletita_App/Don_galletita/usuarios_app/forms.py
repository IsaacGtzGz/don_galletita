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

    # Validación para el campo Teléfono
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            raise ValidationError('El teléfono solo debe contener números.')
        if len(telefono) != 10:
            raise ValidationError('El teléfono debe tener exactamente 10 dígitos.')
        return telefono

    # Validación para los campos de texto (Nombre, Apellido Paterno, Apellido Materno)
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre.isalpha():
            raise ValidationError('El nombre solo debe contener letras.')
        return nombre

    def clean_apellido_paterno(self):
        apellido_paterno = self.cleaned_data.get('apellido_paterno')
        if not apellido_paterno.isalpha():
            raise ValidationError('El apellido paterno solo debe contener letras.')
        return apellido_paterno

    def clean_apellido_materno(self):
        apellido_materno = self.cleaned_data.get('apellido_materno')
        if not apellido_materno.isalpha():
            raise ValidationError('El apellido materno solo debe contener letras.')
        return apellido_materno

    # Validación para la contraseña
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Las contraseñas no coinciden.")

            if len(password2) < 8:
                raise ValidationError("La contraseña debe tener al menos 8 caracteres.")

            if not any(char.isupper() for char in password2):
                raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")

            if not any(char.islower() for char in password2):
                raise ValidationError("La contraseña debe contener al menos una letra minúscula.")

            if not any(char.isdigit() for char in password2):
                raise ValidationError("La contraseña debe contener al menos un número.")

            if not any(char in '!"#$%&/()=?¡¿' for char in password2):
                raise ValidationError("La contraseña debe contener al menos un carácter especial (!\"#$%&/()=?¡¿).")

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

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.nombre = self.cleaned_data['nombre']
        usuario.apellido_paterno = self.cleaned_data['apellido_paterno']
        usuario.apellido_materno = self.cleaned_data['apellido_materno']
        usuario.telefono = self.cleaned_data['telefono']
        usuario.direccion = self.cleaned_data['direccion']
        usuario.rol = self.cleaned_data['rol']
        if commit:
            usuario.save()
        return usuario