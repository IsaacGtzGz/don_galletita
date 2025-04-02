from django import forms
from insumos_app.models import Insumos
from decimal import Decimal

class InsumosRegistrarForm(forms.ModelForm):
    class Meta:
        model = Insumos
        fields = ['nombre_insumo', 'unidad_medida', 'cantidad_disponible']	
        widgets = {
            'nombre_insumo': forms.TextInput(attrs={'class': 'form-control'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_disponible': forms.NumberInput(attrs={'class': 'form-control'})
        }
    def clean_nombre_insumo(self):
        nombre = self.cleaned_data.get('nombre_insumo')
        # Verificar si ya existe un insumo con el mismo nombre
        if Insumos.objects.filter(nombre_insumo__iexact=nombre).exists():
            raise forms.ValidationError(f"El insumo '{nombre}' ya existe en el inventario.")
        return nombre
    
    def clean_cantidad_disponible(self):
        cantidad = self.cleaned_data.get('cantidad_disponible')

        if cantidad < Decimal('0'):
            raise forms.ValidationError("La cantidad disponible no puede ser negativa.")
        return cantidad
    
    def save(self):
        insumo = Insumos(
            nombre_insumo = self.cleaned_data['nombre_insumo'],
            unidad_medida = self.cleaned_data['unidad_medida'],
            cantidad_disponible = self.cleaned_data['cantidad_disponible'])
        insumo.save()
        return insumo
    

    
class InsumosEditarForm(forms.ModelForm):
    class Meta:
        model = Insumos
        fields = ['nombre_insumo', 'unidad_medida', 'cantidad_disponible']
    
    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get('cantidad_disponible')
        unidad = cleaned_data.get('unidad_medida')
        print(f"Datos limpios: Cantidad: {cantidad}, Unidad: {unidad}")
        return cleaned_data
    
    def save(self, commit=True):
        insumo = super().save(commit=False)
        unidad_anterior = insumo.unidad_medida
        insumo.unidad_medida = self.cleaned_data['unidad_medida']

        if unidad_anterior != insumo.unidad_medida:
            insumo.convertir_unidades(insumo.unidad_medida)

        if commit:
            insumo.save()
        return insumo
    