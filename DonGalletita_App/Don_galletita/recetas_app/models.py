from django.db import models
from productos_app.models import Producto

# Create your models here.
class Receta(models.Model):
    receta_id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad_necesaria = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'receta'
        unique_together = ('producto', 'insumo')