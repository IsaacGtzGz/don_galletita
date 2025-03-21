from django import forms
from . import models

class ProveedorRegistrarForm(forms.ModelForm):
    class Meta:
        model = models.Proveedor
        fields = ['nombre', 'telefono', 'direccion', 'dia_entrega']
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "dia_entrega": forms.TextInput(attrs={"class": "form-control"})
        }

    def save(self, commit=True):
        proveedor = super().save(commit=False)
        if commit:
            proveedor.save()
        return proveedor


class ProveedorEditarForm(forms.ModelForm):
    class Meta:
        model = models.Proveedor
        fields = ['nombre', 'telefono', 'direccion', 'dia_entrega']
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "dia_entrega": forms.TextInput(attrs={"class": "form-control"})
        }

    def save(self, id, commit=True):
        proveedor = models.Proveedor.objects.filter(proveedor_id=id).first()
        proveedor.nombre = self.cleaned_data["nombre"]
        proveedor.telefono = self.cleaned_data["telefono"]
        proveedor.direccion = self.cleaned_data["direccion"]
        proveedor.dia_entrega = self.cleaned_data["dia_entrega"]
        if commit:
            proveedor.save()
        return proveedor
