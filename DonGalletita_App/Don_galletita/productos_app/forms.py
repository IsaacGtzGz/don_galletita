from django import forms
from . models import Producto

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
            "fecha_caducidad": forms.DateInput(attrs={"class": "form-control"}),
        }
        