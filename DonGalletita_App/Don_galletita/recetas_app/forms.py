from django import forms
from django.forms import inlineformset_factory
from recetas_app.models import Receta, RecetaInsumo
from insumos_app.models import Insumos
import os
from django.core.files.uploadedfile import UploadedFile

class SelectInsumo(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre_insumo  # Muestra el nombre 
        

class RecetasInsumoForm(forms.ModelForm):
    unidad_medida = forms.CharField(
        required=False,
        label='Unidad de medida',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    class Meta:
        model = RecetaInsumo
        fields = ['insumo', 'cantidad_necesaria']
        widgets = {
            'cantidad_necesaria': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',  # Validación frontend (evita negativos y cero)
                'step': '0.01'  # Permite decimales
            })
        }

    # Sobrescribe el campo insumo para mostrar solo el nombre
    insumo = SelectInsumo(
        queryset=Insumos.objects.all(),
        empty_label="Seleccione un insumo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'insumo' in self.initial:
            id = self.initial['insumo']
            try:
                insumo = Insumos.objects.get(pk=id)
                self.fields['unidad_medida'].initial = insumo.unidad_medida
            except Insumos.DoesNotExist:
                pass
        elif self.instance:
            try:
                if self.instance.insumo:
                    self.fields['unidad_medida'].initial = self.instance.insumo.unidad_medida
            except (AttributeError, Insumos.DoesNotExist):
                pass


    def clean_cantidad_necesaria(self):
        cantidad = self.cleaned_data.get('cantidad_necesaria')
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad necesaria debe ser mayor que cero.")
        return cantidad


# Define el formset factory aquí
RecetasInsumoFormSet = inlineformset_factory(
    Receta,
    RecetaInsumo,
    form=RecetasInsumoForm,
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True,
    fields=('insumo', 'cantidad_necesaria', 'unidad_medida')
)

class RecetasRegistrarForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['producto', 'foto_receta', 'porciones_galletas', 'preparacion']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'foto_receta': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'porciones_galletas': forms.NumberInput(attrs={'class': 'form-control'}),
            'preparacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_producto(self):
        producto = self.cleaned_data.get('producto')
        
        # Verificar si ya existe una receta para este producto
        if Receta.objects.filter(producto=producto).exists():
            raise forms.ValidationError(f"Ya existe una receta para el producto '{producto.nombre}'.")
        return producto

    def clean_porciones_galletas(self):
        porciones = self.cleaned_data.get('porciones_galletas')
        if porciones < 1:
            raise forms.ValidationError("Las porciones deben ser al menos 1.")
        return porciones
    
    def clean_foto_receta(self):
        foto = self.cleaned_data.get('foto_receta')
        if foto:
            # Validar tipo de contenido
            main, sub = foto.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'png']):
                raise forms.ValidationError("Solo se permiten imágenes JPG o PNG.")
            
            # Validar extensión del archivo
            ext = os.path.splitext(foto.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                raise forms.ValidationError("Extensión de archivo no permitida.")
        
        return foto
    
    def clean(self):
        cleaned_data = super().clean()
        preparacion = cleaned_data.get('preparacion')
        producto = cleaned_data.get('producto')
        
        if not preparacion or preparacion.strip() == '':
            self.add_error('preparacion', 'La preparación no puede estar vacía')
            
        if not producto:
            self.add_error('producto', 'Seleccione un producto')
            
        return cleaned_data

    
class RecetaEditarForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['producto', 'foto_receta', 'porciones_galletas', 'preparacion'] 
        widgets = {
            'foto_receta': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'nombre_receta': forms.TextInput(attrs={'class': 'form-control'}),
            'porciones_galletas': forms.NumberInput(attrs={'class': 'form-control'}),
            'preparacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_porciones_galletas(self):
        porciones = self.cleaned_data.get('porciones_galletas')
        if porciones < 1:
            raise forms.ValidationError("Las porciones deben ser al menos 1.")
        return porciones
    
    def clean_foto_receta(self):
        foto = self.cleaned_data.get('foto_receta')
        if foto and isinstance(foto, UploadedFile):  # Verifica si es un archivo cargado
            # Validar tipo de contenido
            main, sub = foto.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'png']):
                raise forms.ValidationError("Solo se permiten imágenes JPG o PNG.")
            
            # Validar extensión del archivo
            ext = os.path.splitext(foto.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                raise forms.ValidationError("Extensión de archivo no permitida.")
        
        return foto
