from django import forms
from django.utils.timezone import now
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
    unidad_medida = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    class Meta:
        model = DetalleCompra
        fields = ['insumo', 'cantidad', 'precio_unitario', 'unidad_medida', 'fecha_caducidad']
        widgets = {
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control"}),
            "fecha_caducidad": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializa el campo unidad_medida si la instancia tiene un insumo asociado
        if self.instance and getattr(self.instance, 'insumo', None):
            self.fields['unidad_medida'].initial = self.instance.insumo.unidad_medida

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is not None and cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser un valor positivo.")
        return cantidad

    def clean_precio_unitario(self):
        precio_unitario = self.cleaned_data.get('precio_unitario')
        if precio_unitario is not None and precio_unitario <= 0:
            raise forms.ValidationError("El precio unitario debe ser un valor positivo.")
        return precio_unitario

    def clean_fecha_caducidad(self):
        fecha_caducidad = self.cleaned_data.get('fecha_caducidad')
        if fecha_caducidad and fecha_caducidad < now().date():
            raise forms.ValidationError("La fecha de caducidad no puede ser anterior a la fecha actual.")
        return fecha_caducidad

    def save(self, commit=True):
        # Antes de guardar, asegura que unidad_medida se actualice según el insumo seleccionado
        instance = super().save(commit=False)
        if instance.insumo:  # Verifica si hay un insumo seleccionado
            instance.unidad_medida = instance.insumo.unidad_medida
        if commit:
            instance.save()
        return instance


DetalleCompraFormSet = inlineformset_factory(
    Compra, DetalleCompra,
    form=DetalleCompraForm,
    fields=['insumo', 'cantidad', 'precio_unitario', 'unidad_medida', 'fecha_caducidad'],
    extra=1, can_delete=False
)