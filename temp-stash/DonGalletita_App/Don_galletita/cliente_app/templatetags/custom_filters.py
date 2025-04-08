from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return 0


@register.filter
def sum_precios(detalles):
    return sum(detalle.precio_unitario * detalle.cantidad for detalle in detalles)
