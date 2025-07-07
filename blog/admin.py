# blog/admin.py
from django.contrib import admin
from .models import Categoria, Post, Comentario

# Opcional: Personalizar cómo se ven los modelos en el panel de administración
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'fecha_publicacion')
    list_filter = ('categoria', 'fecha_publicacion', 'autor')
    search_fields = ('titulo', 'contenido')
    date_hierarchy = 'fecha_publicacion' # Permite navegar por fechas

class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('autor', 'post', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'autor')
    search_fields = ('contenido',)

# Registra tus modelos
admin.site.register(Categoria)
admin.site.register(Post, PostAdmin)
admin.site.register(Comentario, ComentarioAdmin)

# Register your models here.
