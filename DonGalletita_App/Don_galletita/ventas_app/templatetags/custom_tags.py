from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def dias_restantes(fecha):
    """
    Calcula los días restantes desde la fecha proporcionada hasta la fecha actual.
    """
    if not fecha:
        return ""
    
    # Convertir 'timezone.now()' a solo fecha (sin la hora)
    now = timezone.now().date()

    delta = fecha - now
    return delta.days
