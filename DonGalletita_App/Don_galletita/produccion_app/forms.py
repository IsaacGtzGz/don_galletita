from django import forms
from produccion_app.models import Produccion
from recetas_app.models import Receta
class ProduccionForm(forms.ModelForm):
    class Meta:
        model = Produccion
        fields = ['producto']
        
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        
        if not Receta.objects.filter(producto=producto).exists():
            raise forms.ValidationError("El producto no tiene receta registrada")
        
        return cleaned_data