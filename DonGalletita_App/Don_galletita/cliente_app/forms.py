from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinLengthValidator, RegexValidator
from .models import Cliente, DetalleVenta
from usuarios_app.models import Usuario

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Juan'
            }),
            'apellido_paterno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Pérez'
            }),
            'apellido_materno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. López'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10 dígitos'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Calle, número, colonia, ciudad'
            }),
        }
        labels = {
            'nombre': 'Nombre(s)',
            'apellido_paterno': 'Apellido Paterno',
            'apellido_materno': 'Apellido Materno',
        }

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if not telefono.isdigit() or len(telefono) != 10:
            raise forms.ValidationError("El teléfono debe tener 10 dígitos numéricos")
        return telefono

class RegistroClienteForm(UserCreationForm):
    nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        }),
        validators=[
            RegexValidator(
                regex='^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$',
                message='Solo se permiten letras y espacios'
            )
        ]
    )
    apellido_paterno = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido paterno'
        }),
        validators=[
            RegexValidator(
                regex='^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$',
                message='Solo se permiten letras y espacios'
            )
        ]
    )
    apellido_materno = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido materno'
        }),
        validators=[
            RegexValidator(
                regex='^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$',
                message='Solo se permiten letras y espacios'
            )
        ]
    )
    telefono = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '10 dígitos'
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
            'placeholder': 'Dirección completa'
        }),
        required=True
    )

    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'password1', 'password2']
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario único'
            }),
        }
        help_texts = {
            'nombre_usuario': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña'
        })
        # Eliminar campo email si existe
        if 'email' in self.fields:
            del self.fields['email']

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.rol = 'cliente'
        
        if commit:
            usuario.save()
            # Crear el cliente con cliente_id automático
            cliente = Cliente(
                usuario=usuario,
                nombre=self.cleaned_data['nombre'],
                apellido_paterno=self.cleaned_data['apellido_paterno'],
                apellido_materno=self.cleaned_data['apellido_materno'],
                telefono=self.cleaned_data['telefono'],
                direccion=self.cleaned_data['direccion']
            )
            cliente.save()  # Esto generará automáticamente el cliente_id
        
        return usuario
    
    nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        }),
        validators=[
            RegexValidator(
                regex='^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$',
                message='Solo se permiten letras y espacios'
            )
        ]
    )
    apellido_paterno = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido paterno'
        })
    )
    apellido_materno = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido materno'
        })
    )
    telefono = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '10 dígitos'
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
            'placeholder': 'Dirección completa'
        }),
        required=True
    )

    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'password1', 'password2']
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario único'
            }),
        }
        help_texts = {
            'nombre_usuario': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña'
        })

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.rol = 'cliente'
        if commit:
            usuario.save()
            Cliente.objects.create(
                usuario=usuario,
                nombre=self.cleaned_data['nombre'],
                apellido_paterno=self.cleaned_data['apellido_paterno'],
                apellido_materno=self.cleaned_data['apellido_materno'],
                telefono=self.cleaned_data['telefono'],
                direccion=self.cleaned_data['direccion']
            )
        return usuario

class CarritoForm(forms.Form):
    producto_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    unidad_medida = forms.ChoiceField(
        choices=DetalleVenta.unidad_medida,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Unidad de medida'
    )
    cantidad = forms.DecimalField(
        min_value=0.001,
        max_digits=10,
        decimal_places=3,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.001'
        }),
        label='Cantidad'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unidad_medida'].choices = DetalleVenta.UNIDADES_MEDIDA