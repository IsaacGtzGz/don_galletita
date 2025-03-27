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
            'cantidad_disponible': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def clean_nombre_insumo(self):
        nombre = self.cleaned_data.get('nombre_insumo')
        # Verificar si ya existe un insumo con el mismo nombre
        if Insumos.objects.filter(nombre_insumo__iexact=nombre).exists():
            raise forms.ValidationError(f"El insumo '{nombre}' ya existe en el inventario.")
        return nombre
    def clean_cantidad_disponible(self):
        cantidad = self.cleaned_data.get('cantidad_disponible')
        unidad = self.cleaned_data.get('unidad_medida')

        if cantidad < Decimal('0'):
            raise forms.ValidationError("La cantidad disponible no puede ser negativa.")

        # Normalizar valores si es necesario
        if unidad == 'kg':
            cantidad *= Decimal('1000')  # Convertir kg a g
        elif unidad == 'ml':
            cantidad /= Decimal('1000')  # Convertir ml a l

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
    
    def save(self, commit=True):
        insumo = self.instance
        nueva_unidad = self.cleaned_data['unidad_medida']

        # Detectar si la unidad cambió
        if insumo.unidad_medida != nueva_unidad:
            print(f"Realizando conversión de {insumo.unidad_medida} a {nueva_unidad}...")
            insumo.convertir_unidades(nueva_unidad)

        insumo.nombre_insumo = self.cleaned_data['nombre_insumo']
        print(f"Después de la conversión: {insumo.cantidad_disponible} {insumo.unidad_medida}")

        if commit:
            insumo.save()
        return insumo
    