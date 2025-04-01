from django import forms
from . import models

class CompraRegistrarForm(forms.ModelForm):
    class Meta:
        model = models.Compra
        fields = ['proveedor', 'insumo', 'cantidad', 'precio_unitario', 'unidad_medida', 'fecha_caducidad']
        widgets = {
            "proveedor": forms.Select(attrs={"class": "form-control"}),
            "insumo": forms.Select(attrs={"class": "form-control"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control"}),
            "unidad_medida": forms.Select(attrs={"class": "form-control"}),
            "fecha_caducidad": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def save(self, commit=True):
        compra = super().save(commit=False)
        if commit:
            compra.save()
        return compra


class CompraEditarForm(forms.ModelForm):
    class Meta:
        model = models.Compra
        fields = ['proveedor', 'insumo', 'cantidad', 'precio_unitario', 'unidad_medida', 'fecha_caducidad']
        widgets = {
            "proveedor": forms.Select(attrs={"class": "form-control"}),
            "insumo": forms.Select(attrs={"class": "form-control"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control"}),
            "unidad_medida": forms.Select(attrs={"class": "form-control"}),
            "fecha_caducidad": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def save(self, id, commit=True):
        compra = models.Compra.objects.filter(compra_id=id).first()
        compra.proveedor = self.cleaned_data["proveedor"]
        compra.insumo = self.cleaned_data["insumo"]
        compra.cantidad = self.cleaned_data["cantidad"]
        compra.precio_unitario = self.cleaned_data["precio_unitario"]
        compra.unidad_medida = self.cleaned_data["unidad_medida"]
        compra.fecha_caducidad = self.cleaned_data["fecha_caducidad"]
        if commit:
            compra.save()
        return compra
