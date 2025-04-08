from django.db import models
from insumos_app.models import Insumos
from productos_app.models import Producto
from django.core.exceptions import ValidationError

def validate_image_extension(value):
    valid_extensions = ['.jpg', '.jpeg', '.png']
    if not any(value.name.endswith(ext) for ext in valid_extensions):
        raise ValidationError('El archivo debe ser una imagen en formato JPG, JPEG o PNG.')

class Receta(models.Model):
    receta_id = models.AutoField(primary_key=True)
    producto = producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    foto_receta = models.ImageField(
        upload_to='recetas/', 
        null=True, 
        blank=True,
        validators=[validate_image_extension])
    preparacion = models.TextField(default="Sin descripción")
    porciones_galletas = models.IntegerField(default=1)

    def get_receta_id(self):
        return self.receta_id
 
    def _str_(self):
        return f"Receta {self.receta_id}-{self.producto.nombre}"

class RecetaInsumo(models.Model):
    recetasinsumo_id = models.AutoField(primary_key=True)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumos, on_delete=models.CASCADE)
    cantidad_necesaria = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    def _str_(self):
        return f"{self.recetasinsumo_id}-{self.receta.producto.nombre}-{self.insumo.nombre_insumo}-{self.cantidad_necesaria}"