from django import forms
from .models import Venta, DetalleVenta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['persona', 'estatus_venta']
        widgets = {
            'persona': forms.Select(attrs={'class': 'form-control'}),
            'estatus_venta': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        venta = super().save(commit=False)
        if commit:
            venta.save()
        return venta


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'unidad_medida', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def save(self, commit=True):
        detalle_venta = super().save(commit=False)
        if commit:
            detalle_venta.save()
        return detalle_venta
