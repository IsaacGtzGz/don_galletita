from django import forms
from .models import Producto
from django.core.exceptions import ValidationError
from django.utils import timezone

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'unidad_medida', 'cantidad_disponible', 'precio_unitario', 'peso_unidad', 'fecha_caducidad', 'imagen_producto']
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control"}),
            "unidad_medida": forms.Select(attrs={"class": "form-control"}),
            "cantidad_disponible": forms.NumberInput(attrs={"class": "form-control"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control"}),
            "peso_unidad": forms.NumberInput(attrs={"class": "form-control"}),
            "fecha_caducidad": forms.DateInput(attrs={"class": "form-control","type": "date",  # Esto activará el date picker nativo
                    "min": timezone.now().date().isoformat()  # Fecha mínima hoy
                }
            ),
            "imagen_producto": forms.FileInput(attrs={"class": "form-control"}), 
                        "cantidad_disponible": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",  # Asegura que el valor mínimo sea 1
                "step": "1"  # Solo permite números enteros
            }),
            "precio_unitario": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0.01",  # Asegura que el valor mínimo sea 0.01
                "step": "0.01"  # Permite decimales
            }),
            "peso_unidad": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0.01",  # Asegura que el valor mínimo sea 0.01
                "step": "0.01"  # Permite decimales
            }),

        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        # Validación para asegurarse de que el nombre sea único
        if Producto.objects.filter(nombre__iexact=nombre).exists():
            if self.instance.pk is None:  # Solo validar si es una creación
                raise ValidationError('Este nombre de producto ya existe')
        return nombre.strip().title()

    def clean_fecha_caducidad(self):
        fecha = self.cleaned_data['fecha_caducidad']
        if fecha and fecha < timezone.now().date():
            raise ValidationError('La fecha de caducidad no puede ser en el pasado')
        return fecha
    def clean_cantidad_disponible(self):
        cantidad = self.cleaned_data['cantidad_disponible']
        if cantidad < 1:
            raise ValidationError('La cantidad debe ser al menos 1')
        return cantidad

    def clean_precio_unitario(self):
        precio = self.cleaned_data['precio_unitario']
        if precio <= 0:
            raise ValidationError('El precio debe ser mayor que 0')
        return precio

    def clean_peso_unidad(self):
        peso = self.cleaned_data['peso_unidad']
        if peso <= 0:
            raise ValidationError('El peso debe ser mayor que 0')
        return peso