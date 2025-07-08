# blog/templatetags/blog_tags.py
from django import template
from django.urls import reverse
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def url_with_params(view_name, current_params, param_to_change, new_value):
    """
    Genera una URL para una vista, manteniendo los parámetros GET existentes
    y actualizando o añadiendo un parámetro específico.
    """
    # Copia los parámetros actuales para no modificar el QueryDict original
    updated_params = current_params.copy()

    # Actualiza o añade el parámetro deseado
    if new_value is None or new_value == '':
        if param_to_change in updated_params:
            del updated_params[param_to_change] # Elimina el parámetro si el nuevo valor es nulo/vacío
    else:
        updated_params[param_to_change] = new_value

    # Elimina el parámetro 'page' si estamos cambiando la ordenación o un filtro
    # para que siempre se vaya a la primera página al aplicar un nuevo filtro/orden
    if param_to_change != 'page' and 'page' in updated_params:
        del updated_params['page']

    # Construye la parte de la query string
    query_string = updated_params.urlencode()

    # Genera la URL base de la vista
    base_url = reverse(view_name)

    # Combina la URL base con la query string si existe
    if query_string:
        return f"{base_url}?{query_string}"
    return base_url