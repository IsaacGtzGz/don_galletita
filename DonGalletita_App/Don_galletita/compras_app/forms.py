from django import forms
from django.forms.models import inlineformset_factory
from .models import Compra, DetalleCompra

class CompraRegistrarForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor']
        widgets = {
            "proveedor": forms.Select(attrs={"class": "form-control"}),
        }

class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['insumo', 'cantidad', 'precio_unitario', 'unidad_medida', 'fecha_caducidad']
        widgets = {
            "insumo": forms.Select(attrs={"class": "form-control"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control"}),
            "unidad_medida": forms.Select(attrs={"class": "form-control"}),
            "fecha_caducidad": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

DetalleCompraFormSet = inlineformset_factory(
    Compra, DetalleCompra, 
    fields=['insumo', 'cantidad', 'precio_unitario', 'unidad_medida', 'fecha_caducidad'], 
    extra=1, can_delete=True
)