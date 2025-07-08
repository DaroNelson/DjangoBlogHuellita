# blog/context_processors.py
from .models import Categoria

def categorias_globales(request):
    """
    Context processor para inyectar todas las categorías en el contexto de la plantilla.
    """
    return {
        'categorias': Categoria.objects.all()
    }