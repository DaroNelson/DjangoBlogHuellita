# blog/models.py
from django.db import models
from django.contrib.auth.models import User # Importamos el modelo de usuario de Django

# Modelo para las categorías de los posts
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True) # unique=True asegura que no haya categorías con el mismo nombre

    class Meta:
        verbose_name_plural = "Categorías" # Para que se muestre bien en el admin

    def __str__(self):
        return self.nombre

# Modelo para los posts del blog
class Post(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True) # Se establece automáticamente al crear el post
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts') # Un post pertenece a un usuario. Si el usuario se elimina, sus posts también.
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True) # Un post puede tener una categoría. Si la categoría se elimina, el campo se pone a NULL.
    imagen_portada = models.ImageField(upload_to='post_images/', null=True, blank=True) # Opcional: permite subir imágenes

    class Meta:
        ordering = ['-fecha_publicacion'] # Por defecto, los posts se ordenarán del más nuevo al más viejo

    def __str__(self):
        return self.titulo

# Modelo para los comentarios de los posts
class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios') # Un comentario pertenece a un post. Si el post se elimina, sus comentarios también.
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios') # Un comentario es hecho por un usuario.
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True) # Se establece automáticamente al crear el comentario

    class Meta:
        ordering = ['fecha_creacion'] # Ordenar comentarios por fecha de creación

    def __str__(self):
        return f'Comentario de {self.autor.username} en {self.post.titulo[:50]}...' # Muestra los primeros 50 caracteres del título del post
    
    # Create your models here.
