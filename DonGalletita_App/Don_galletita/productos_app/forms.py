from django import forms
from .models import Producto
from django.core.exceptions import ValidationError
from django.utils import timezone

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'unidad_medida', 'cantidad_disponible', 'precio_unitario', 'peso_unidad', 'fecha_caducidad']
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
