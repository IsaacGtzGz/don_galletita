from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Produccion, LoteProduccion, ConsumoInsumos
from productos_app.models import Producto
from recetas_app.models import Receta
from django.db import transaction



# Create your views here.
@transaction.atomic
def iniciar_produccion(request, producto_id, cantidad_galletas):
    producto = Producto.objects.get(pk=producto_id)
    recetas = Receta.objects.filter(producto_id=producto_id)
    
    # Verificar insumos suficientes
    for receta in recetas:
        insumo = receta.insumo
        cantidad_necesaria = receta.cantidad_necesaria * cantidad_galletas
        
        
        if insumo.cantidad_disponible < cantidad_necesaria:
            raise Exception(f"Insumo {insumo.nombre_insumo} insuficiente")

    # Crear producción
    produccion = Produccion.objects.create(producto=producto)
    
    # Registrar consumo de insumos
    for receta in recetas:
        cantidad_usada = receta.cantidad_necesaria * cantidad_galletas
        ConsumoInsumos.objects.create(
            produccion=produccion,
            insumo=receta.insumo,
            cantidad_usada=cantidad_usada
        )
        # Actualizar inventario
        receta.insumo.cantidad_disponible -= cantidad_usada
        receta.insumo.save()
    
    return produccion

def finalizar_produccion(request, produccion_id):
    produccion = Produccion.objects.get(pk=produccion_id)
    produccion.fecha_finalizacion = timezone.now()
    produccion.estado = 'finalizada'
    produccion.save()
    
    # Calcular fecha de caducidad (ejemplo: 30 días desde producción)
    fecha_caducidad = timezone.now() + timedelta(days=30)
    
    # Crear lote
    lote = LoteProduccion.objects.create(
        produccion=produccion,
        cantidad_galletas=1000,  # Obtener de la receta
        fecha_caducidad=fecha_caducidad
    )
    
    # Actualizar inventario de producto
    producto = produccion.producto
    producto.cantidad_disponible += lote.cantidad_galletas
    producto.fecha_caducidad = fecha_caducidad
    producto.save()
    
    return lote