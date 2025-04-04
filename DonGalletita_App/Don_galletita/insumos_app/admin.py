from django.contrib import admin

# Register your models here.
# admin.py
class InsumosAdmin(admin.ModelAdmin):
    list_display = ('nombre_insumo', 'unidad_medida', 'get_cantidad')
    
    def get_cantidad(self, obj):
        return f"{float(obj.cantidad_disponible):.3f} {obj.unidad_medida}"
    get_cantidad.short_description = 'Cantidad Disponible'