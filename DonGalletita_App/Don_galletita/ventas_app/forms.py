from django import forms
from .models import Venta, DetalleVenta
from productos_app.models import Producto
from django.core.exceptions import ValidationError

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['persona', 'estatus_venta']
        widgets = {
            'persona': forms.Select(attrs={'class': 'form-control'}),
            'estatus_venta': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Si es una nueva instancia (crear venta)
            self.fields['estatus_venta'].widget.attrs['disabled'] = True  # Deshabilitar el campo
            self.initial['estatus_venta'] = 'Pendiente'  # Establecer valor inicial

    def clean_estatus_venta(self):
        if self.instance.pk:  # Si la venta ya existe
            venta_anterior = Venta.objects.get(pk=self.instance.pk)
            if venta_anterior.estatus_venta == 'Pagado':
                if self.cleaned_data['estatus_venta'] not in ['Pagado', 'Cancelado']:
                    raise forms.ValidationError("No se puede cambiar el estatus de 'Pagado' a otro que no sea 'Cancelado'.")
                if not venta_anterior.ticket:
                    raise forms.ValidationError("No se puede cambiar el estatus de 'Pagado' si el ticket no ha sido generado.")
        return self.cleaned_data['estatus_venta']

    def save(self, commit=True):
        venta = super().save(commit=False)
        if not self.instance.pk:  # Si es una nueva instancia (crear venta)
            venta.estatus_venta = 'Pendiente'
        if commit:
            venta.save()
        return venta

    def is_valid(self):
        if not self.instance.pk:  # Si es una nueva instancia (crear venta)
            self.data = self.data.copy()
            self.data['estatus_venta'] = 'Pendiente'  # Forzar el valor en los datos del formulario
        return super().is_valid()

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'unidad_medida', 'cantidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.all()
        self.fields['unidad_medida'].choices = [
            ('pz', 'Piezas'),
            ('g', 'Gramos'),
            ('1kg', '1kg'),
            ('700gr', '700gr')
        ]

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        unidad_medida = cleaned_data.get('unidad_medida')
        cantidad = cleaned_data.get('cantidad')

        if cantidad < 1:
            raise ValidationError("La cantidad debe ser mayor o igual a 1.")

        if unidad_medida == 'g' and cantidad < producto.peso_unidad:
            raise ValidationError(f"El gramaje mínimo debe ser igual o mayor al peso de una galleta ({producto.peso_unidad}g).")

        if unidad_medida in ['1kg', '700gr']:
            peso_total = 1000 if unidad_medida == '1kg' else 700
            piezas_necesarias = peso_total / producto.peso_unidad
            if producto.cantidad_disponible < piezas_necesarias * cantidad:
                raise ValidationError("No hay suficiente inventario para esta venta.")

        if unidad_medida == 'g':
            piezas_necesarias = cantidad / producto.peso_unidad
            if producto.cantidad_disponible < piezas_necesarias:
                raise ValidationError(f"Stock insuficiente para el producto {producto.nombre}. Seleccione una cantidad válida.")

        return cleaned_data