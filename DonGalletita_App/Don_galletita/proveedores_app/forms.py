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

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if any(char.isdigit() for char in nombre):
            raise forms.ValidationError("El nombre no puede contener números.")
        return nombre

    def clean_apellido_paterno(self):
        apellido_paterno = self.cleaned_data.get('apellido_paterno')
        if any(char.isdigit() for char in apellido_paterno):
            raise forms.ValidationError("El apellido paterno no puede contener números.")
        return apellido_paterno

    def clean_apellido_materno(self):
        apellido_materno = self.cleaned_data.get('apellido_materno')
        if any(char.isdigit() for char in apellido_materno):
            raise forms.ValidationError("El apellido materno no puede contener números.")
        return apellido_materno

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            raise forms.ValidationError("El número de teléfono solo puede contener dígitos.")
        if len(telefono) != 10:
            raise forms.ValidationError("El número de teléfono debe tener exactamente 10 caracteres.")
        return telefono

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

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if any(char.isdigit() for char in nombre):
            raise forms.ValidationError("El nombre no puede contener números.")
        return nombre

    def clean_apellido_paterno(self):
        apellido_paterno = self.cleaned_data.get('apellido_paterno')
        if any(char.isdigit() for char in apellido_paterno):
            raise forms.ValidationError("El apellido paterno no puede contener números.")
        return apellido_paterno

    def clean_apellido_materno(self):
        apellido_materno = self.cleaned_data.get('apellido_materno')
        if any(char.isdigit() for char in apellido_materno):
            raise forms.ValidationError("El apellido materno no puede contener números.")
        return apellido_materno

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            raise forms.ValidationError("El número de teléfono solo puede contener dígitos.")
        if len(telefono) != 10:
            raise forms.ValidationError("El número de teléfono debe tener exactamente 10 caracteres.")
        return telefono

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
