from django import forms
from . import models

class ProveedorRegistrarForm(forms.ModelForm):
    class Meta:
        model = models.Proveedor
        fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'telefono', 'direccion']
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido_paterno": forms.TextInput(attrs={"class": "form-control"}),
            "apellido_materno": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        proveedor = super().save(commit=False)
        if commit:
            proveedor.save()
        return proveedor


class ProveedorEditarForm(forms.ModelForm):
    class Meta:
        model = models.Proveedor
        fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'telefono', 'direccion']
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido_paterno": forms.TextInput(attrs={"class": "form-control"}),
            "apellido_materno": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
        }

    def save(self, id, commit=True):
        proveedor = models.Proveedor.objects.filter(proveedor_id=id).first()
        proveedor.nombre = self.cleaned_data["nombre"]
        proveedor.apellido_paterno = self.cleaned_data["apellido_paterno"]
        proveedor.apellido_materno = self.cleaned_data["apellido_materno"]
        proveedor.telefono = self.cleaned_data["telefono"]
        proveedor.direccion = self.cleaned_data["direccion"]
        if commit:
            proveedor.save()
        return proveedor
