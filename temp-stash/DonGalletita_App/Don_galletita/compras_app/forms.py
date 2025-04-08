from django import forms
from django.forms.models import inlineformset_factory
from .models import Compra, DetalleCompra, Insumos, Proveedor


class SelectProveedor(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre  # Ajusta según el atributo correcto del modelo Proveedor


class SelectInsumo(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre_insumo


class CompraRegistrarForm(forms.ModelForm):
    proveedor = SelectProveedor(
        queryset=Proveedor.objects.all(),
        empty_label="Seleccione un proveedor",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Compra
        fields = ['proveedor']
        widgets = {
            "proveedor": forms.Select(attrs={"class": "form-control"}),
        }


class DetalleCompraForm(forms.ModelForm):
    # Sobrescribe el campo insumo para mostrar solo el nombre
    insumo = SelectInsumo(
        queryset=Insumos.objects.all(),
        empty_label="Seleccione un insumo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = DetalleCompra
        fields = ['insumo', 'cantidad', 'precio_unitario', 'unidad_medida', 'fecha_caducidad']
        widgets = {
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control"}),
            "unidad_medida": forms.Select(attrs={"class": "form-control"}),
            "fecha_caducidad": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


DetalleCompraFormSet = inlineformset_factory(
    Compra, DetalleCompra,
    form=DetalleCompraForm,
    fields=['insumo', 'cantidad', 'precio_unitario', 'unidad_medida', 'fecha_caducidad'],
    extra=1, can_delete=False
)