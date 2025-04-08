from django import forms
from produccion_app.models import Produccion, LoteProduccion
from recetas_app.models import Receta

class ProduccionForm(forms.ModelForm):
    cantidad_producida = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Produccion
        fields = ['producto', 'cantidad_producida', 'fecha_finalizacion']
        widgets = {
            "producto": forms.Select(attrs={"class": "form-control"}),
            "fecha_finalizacion": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            )
        }
        
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad_producida')
        
        if not Receta.objects.filter(producto=producto).exists():
            raise forms.ValidationError("El producto no tiene receta registrada")
            
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad producida debe ser mayor a cero")
            
        return cleaned_data

class LoteProduccionForm(forms.ModelForm):
    class Meta:
        model = LoteProduccion
        fields = ['cantidad_galletas', 'fecha_caducidad']
        widgets = {
            'fecha_caducidad': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cantidad_galletas': forms.NumberInput(attrs={'class': 'form-control'})
        }