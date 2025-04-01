from django import forms
from .models import Compra, DetalleCompra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor', 'fecha_compra']
        widgets = {
            'fecha_compra': forms.DateInput(attrs={'type': 'date'}),
        }


class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['insumo', 'cantidad', 'unidad', 'precio', 'fecha_caducidad']
        widgets = {
            'fecha_caducidad': forms.DateInput(attrs={'type': 'date'}),
        }