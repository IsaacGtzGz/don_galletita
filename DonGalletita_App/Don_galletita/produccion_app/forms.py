from django import forms
from produccion_app.models import Produccion, LoteProduccion
from recetas_app.models import Receta
from django.utils.timezone import now
from django import forms
from .models import Produccion
from recetas_app.models import Receta

# produccion_app/forms.py
# forms.py - Modifica el formulario para que coincida con el HTML
class ProduccionForm(forms.ModelForm):
    receta_id = forms.ModelChoiceField(
        queryset=Receta.objects.filter(producto__isnull=False),
        label="Receta",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    porciones_galletas = forms.IntegerField(
        label="Cantidad a producir",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True})
    )

    class Meta:
        model = Produccion
        fields = ['fecha_finalizacion']  # Los otros campos los manejamos manualmente
        widgets = {
            'fecha_finalizacion': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_finalizacion = cleaned_data.get('fecha_finalizacion')

        if fecha_inicio and fecha_finalizacion and fecha_finalizacion < fecha_inicio:
            raise forms.ValidationError("La fecha de finalización no puede ser anterior a la fecha de inicio.")


class LoteProduccionForm(forms.ModelForm):
    class Meta:
        model = LoteProduccion
        fields = ['cantidad_galletas', 'fecha_caducidad']
        widgets = {
            'fecha_caducidad': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cantidad_galletas': forms.NumberInput(attrs={'class': 'form-control'})
        }