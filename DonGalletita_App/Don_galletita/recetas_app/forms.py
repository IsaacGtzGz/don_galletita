from django import forms
from django.forms import inlineformset_factory
from recetas_app.models import Recetas, RecetaInsumo
from insumos_app.models import Insumos

class SelectInsumo(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre_insumo

class RecetasInsumoForm(forms.ModelForm):
    class Meta:
        model = RecetaInsumo
        fields = ['insumo','cantidad_necesaria', 'unidad_medida']
        widgets = {
            'insumo': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_necesaria': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-control', 'readonly': True}),	
        }

# Sobrescribe el campo insumo para mostrar solo el nombre
    insumo = SelectInsumo(
        queryset=Insumos.objects.all(),
        empty_label="Seleccione un insumo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


# Define el formset factory aquí
RecetasInsumoFormSet = inlineformset_factory(
    Recetas,
    RecetaInsumo,
    form=RecetasInsumoForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)

class RecetasRegistrarForm(forms.ModelForm):
    class Meta:
        model = Recetas
        fields = ['foto_receta','nombre_receta','porciones_galletas','preparacion']
        widgets = {
            'foto_receta': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'nombre_receta': forms.TextInput(attrs={'class': 'form-control'}),
            'porciones_galletas': forms.NumberInput(attrs={'class': 'form-control'}),
            'preparacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    
class RecetaEditarForm(forms.ModelForm):
    class Meta:
        model = Recetas
        fields = ['foto_receta', 'nombre_receta', 'porciones_galletas', 'preparacion']
        widgets = {
            'foto_receta': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'nombre_receta': forms.TextInput(attrs={'class': 'form-control'}),
            'porciones_galletas': forms.NumberInput(attrs={'class': 'form-control'}),
            'preparacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Opcional: personalizaciones adicionales al inicializar
        self.fields['foto_receta'].required = False