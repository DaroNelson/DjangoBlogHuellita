# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Categoria, Comentario
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm # Para el registro
from django.contrib import messages # Para mostrar mensajes al usuario

# Vista para la página principal (listar posts)
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html' # Ruta a tu plantilla HTML
    context_object_name = 'posts' # Nombre de la variable que se pasará a la plantilla
    paginate_by = 5 # Opcional: para paginar los resultados

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrado por categoría
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria__nombre=categoria)

        # Filtrado por fecha (ejemplo básico, se puede mejorar)
        fecha = self.request.GET.get('fecha')
        if fecha:
            # Puedes parsear la fecha y filtrar por año, mes, etc.
            # Por ahora, un ejemplo simple:
            queryset = queryset.filter(fecha_publicacion__date=fecha)

        # Filtrado por comentarios (ejemplo: posts con al menos 1 comentario)
        comentarios = self.request.GET.get('comentarios')
        if comentarios == 'si':
            queryset = queryset.filter(comentarios__isnull=False).distinct()
        elif comentarios == 'no':
            queryset = queryset.filter(comentarios__isnull=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all() # Pasar todas las categorías para el filtro
        return context


# Vista para ver el detalle de un post
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aquí puedes agregar el formulario de comentarios si el usuario está autenticado
        return context

# Vista para crear un nuevo post
class PostCreateView(LoginRequiredMixin, CreateView): # Requiere que el usuario esté logueado
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['titulo', 'contenido', 'categoria', 'imagen_portada'] # Campos que el usuario puede editar

    def form_valid(self, form):
        form.instance.autor = self.request.user # Asigna el usuario logueado como autor
        messages.success(self.request, '¡Tu post ha sido creado exitosamente!')
        return super().form_valid(form)

    success_url = reverse_lazy('post_list') # Redirige a la lista de posts después de crear

# Vista para actualizar un post existente
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView): # Requiere logueo y que el usuario sea el autor
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['titulo', 'contenido', 'categoria', 'imagen_portada']

    def form_valid(self, form):
        form.instance.autor = self.request.user
        messages.success(self.request, '¡Tu post ha sido actualizado exitosamente!')
        return super().form_valid(form)

    def test_func(self): # Solo permite al autor del post editarlo
        post = self.get_object()
        return self.request.user == post.autor

    success_url = reverse_lazy('post_list')

# Vista para eliminar un post
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView): # Requiere logueo y que el usuario sea el autor
    model = Post
    template_name = 'blog/post_confirm_delete.html' # Plantilla para confirmar la eliminación
    context_object_name = 'post'
    success_url = reverse_lazy('post_list') # Redirige a la lista de posts después de eliminar

    def test_func(self): # Solo permite al autor del post eliminarlo (o al admin)
        post = self.get_object()
        # Permite eliminar si es el autor O si es superusuario (admin)
        return self.request.user == post.autor or self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '¡El post ha sido eliminado exitosamente!')
        return super().delete(request, *args, **kwargs)

# Vista para registrar nuevos usuarios
class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login') # Redirige a la página de login después del registro

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '¡Registro exitoso! Ya puedes iniciar sesión.')
        return response

# Vista para añadir un comentario (usaremos una función simple por ahora)
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json

@login_required # Solo usuarios logueados pueden comentar
@require_POST # Solo acepta peticiones POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    data = json.loads(request.body)
    content = data.get('content')

    if content:
        Comentario.objects.create(post=post, autor=request.user, contenido=content)
        messages.success(request, '¡Tu comentario ha sido añadido!')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'El contenido del comentario no puede estar vacío.'}, status=400)
# Create your views here.

