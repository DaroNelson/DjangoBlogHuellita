# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Post, Categoria, Comentario, Like
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
#from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages # Para mostrar mensajes al usuario
from django.core.mail import send_mail # Importar para enviar correos
from django.conf import settings # Importar para acceder a settings como EMAIL_HOST_USER
#from django.http import JsonResponse # Posiblemente lo usaremos más adelante para Likes con AJAX


from .forms import ContactForm, ComentarioForm, CustomUserCreationForm # Importa tu nuevo formulario
import urllib.parse #Whatsapp

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
            
        # --- Lógica de Ordenación (NUEVA/REINTRODUCIDA) ---
        # Definimos un orden por defecto si no se especifica ninguno
        # Por ejemplo, los posts más recientes primero
        order_by = self.request.GET.get('order_by', '-fecha_publicacion')

        if order_by == 'antiguedad_asc':
            queryset = queryset.order_by('fecha_publicacion') # Los más antiguos primero
        elif order_by == 'antiguedad_desc':
            queryset = queryset.order_by('-fecha_publicacion') # Los más recientes primero
        elif order_by == 'titulo_asc':
            queryset = queryset.order_by('titulo') # Orden alfabético ascendente por título
        elif order_by == 'titulo_desc':
            queryset = queryset.order_by('-titulo') # Orden alfabético descendente por título
        else:
            # Si el parámetro no es reconocido o es un valor por defecto no listado,
            # asegura un orden por defecto para evitar resultados inconsistentes
            queryset = queryset.order_by('-fecha_publicacion')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasamos los parámetros GET actuales para que la plantilla pueda construir URLs
        # que mantengan los filtros y la ordenación
        context['current_get_params'] = self.request.GET.copy()
        
        return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['categorias'] = Categoria.objects.all() # Pasar todas las categorías para el filtro
    #     return context


# Vista para ver el detalle de un post
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pasa una nueva instancia del formulario de comentarios al contexto
        context['comment_form'] = ComentarioForm()

        # Lógica para verificar si el usuario actual le dio "Me gusta" al post
        user_has_liked = False
        if self.request.user.is_authenticated:
            # Comprueba si existe un objeto Like para este post y el usuario autenticado
            user_has_liked = Like.objects.filter(post=self.object, user=self.request.user).exists()
        
        context['user_has_liked'] = user_has_liked
        
        # Asegúrate de pasar las categorías globales si las necesitas en tu base.html o navbar
        # (solo si no usas un context processor para ellas)
        # context['categorias_globales'] = Categoria.objects.all() # Esto es redundante si ya tienes un context processor

        return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # Aquí puedes agregar el formulario de comentarios si el usuario está autenticado
    #     return context
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['categorias'] = Categoria.objects.all() # Pasar todas las categorías para el filtro
    #     return context


# Vista para crear un nuevo post
class PostCreateView(LoginRequiredMixin, CreateView): # Requiere que el usuario esté logueado
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['titulo', 'contenido', 'categoria', 'imagen_portada'] # Campos que el usuario puede editar

    def form_valid(self, form):
        form.instance.autor = self.request.user # Asigna el usuario logueado como autor
        messages.success(self.request, '¡Tu post ha sido creado exitosamente!')
        return super().form_valid(form)
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['categorias'] = Categoria.objects.all() # Pasar todas las categorías para el filtro
    #     return context

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

    def test_func(self): # Permite al autor del post o al superusuario editarlo
        post = self.get_object()
        return self.request.user == post.autor or self.request.user.is_superuser
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['categorias'] = Categoria.objects.all() # Pasar todas las categorías para el filtro
    #     return context

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
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['categorias'] = Categoria.objects.all() # Pasar todas las categorías para el filtro
    #     return context

# Vista para registrar nuevos usuarios
class RegisterView(CreateView):
    form_class = CustomUserCreationForm # ¡ASEGÚRATE DE QUE ESTA LÍNEA USE CustomUserCreationForm!
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '¡Registro exitoso! Ya puedes iniciar sesión.')
        return response
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['categorias'] = Categoria.objects.all() # Pasar todas las categorías para el filtro
    #     return context
    
def about_view(request):
    """
    Vista para la página 'Acerca de'.
    Proporciona información sobre el blog y su propósito.
    """
    return render(request,'blog/about.html')
    
def contact_view(request):
    """
    Vista para la página de contacto con un formulario.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']
            asunto = form.cleaned_data['asunto']
            mensaje = form.cleaned_data['mensaje']

            # Construye el mensaje de correo
            email_subject = f'Mensaje de Contacto del Blog: {asunto}'
            email_message = f'De: {nombre} <{correo}>\n\n{mensaje}'

            try:
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com', # Remitente del correo
                    ['johanna_contreras@hotmail.com'], # ¡CAMBIA ESTO! La dirección a la que quieres recibir los mensajes
                    fail_silently=False,
                )
                messages.success(request, '¡Gracias! Tu mensaje ha sido enviado correctamente. Te responderemos pronto.')
                return redirect('contact') # Redirige a la misma página para limpiar el formulario
            except Exception as e:
                messages.error(request, f'Hubo un error al enviar tu mensaje. Por favor, inténtalo de nuevo más tarde. ({e})')
    else:
        form = ContactForm() # Crea un formulario vacío para peticiones GET

    context = {
        'form': form,
        'email_contacto': 'contacto@tu_blog.com', # ¡CAMBIA ESTO! Dirección de correo para mostrar
        'instagram_link': 'https://www.instagram.com/tu_usuario_instagram/', # ¡CAMBIA ESTO!
        'tiktok_link': 'https://www.tiktok.com/@tu_usuario_tiktok/', # ¡CAMBIA ESTO!
    }
    return render(request, 'blog/contact.html', context)


def donations_view(request):
    """
    Vista para la página de donaciones, mostrando solo los datos de cuenta.
    """
    # Datos de la cuenta bancaria para mostrar
    datos_cuenta = {
        'banco': 'Banco Ejemplo S.A.',
        'tipo_cuenta': 'Caja de Ahorro', # Opcional, si quieres incluirlo
        'numero_cuenta': '1234-5678-90123456-789', # Número de cuenta completo
        'alias_cbu': 'MI.BLOG.DONA',
        'cbu': '0000000000000000000000', # 22 dígitos CBU
        'cuil_titular': '20-12345678-9', # Alias del alias
        'nombre_titular': 'Nombre de Tu Entidad/Persona',
    }

    # Crear el mensaje de WhatsApp
    mensaje_whatsapp = (
        f"¡Hola! Te comparto los datos de la cuenta para donaciones:\n\n"
        f"🏦 Banco: {datos_cuenta['banco']}\n"
        f"🔢 Número de Cuenta: {datos_cuenta['numero_cuenta']}\n"
        f"✨ Alias: {datos_cuenta['alias_cbu']}\n"
        f"🔗 CBU: {datos_cuenta['cbu']}\n"
        f"🆔 CUIL: {datos_cuenta['cuil_titular']}\n"
        f"👤 Titular: {datos_cuenta['nombre_titular']}\n\n"
        f"¡Gracias por tu apoyo!"
    )
    # Codificar el mensaje para URL de WhatsApp
    whatsapp_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(mensaje_whatsapp)}"

    context = {
        'datos_cuenta': datos_cuenta,
        'whatsapp_url': whatsapp_url,
    }
    return render(request, 'blog/donations.html', context)   

#probando agregar la vista de categorías
class CategoryOverviewView(View):
    """
    Vista que muestra una página con todas las categorías y los últimos 4 posts de cada una.
    """
    template_name = 'blog/category_overview.html'

    def get(self, request, *args, **kwargs):
        categorias = Categoria.objects.all().order_by('nombre') # Ordenar categorías por nombre

        categories_data = []
        for categoria in categorias:
            # Obtener los últimos 4 posts para esta categoría
            # Usamos select_related('autor', 'categoria') para optimizar las consultas a la base de datos
            # cuando accedamos a post.autor.username o post.categoria.nombre en la plantilla.
            # Prefetch_related('likes') para optimizar el conteo de likes si lo necesitas.
            # Puedes ajustar el número de posts (4)
            posts_for_category = Post.objects.filter(categoria=categoria).order_by('-fecha_publicacion')[:4]
            
            categories_data.append({
                'category_object': categoria,
                'posts': posts_for_category
            })
        
        context = {
            'categories_data': categories_data
        }
        return render(request, self.template_name, context)


def like_post(request, pk):
    """
    Vista para manejar los 'Me gusta' de los posts.
    Si el usuario ya dio like, lo remueve. Si no, lo añade.
    Requiere que el usuario esté autenticado.
    """
    # Asegúrate de que el usuario esté autenticado
    if not request.user.is_authenticated:
        messages.warning(request, "Necesitas iniciar sesión para dar Me Gusta.")
        return redirect('login') # Redirige a la página de login

    post = get_object_or_404(Post, pk=pk)

    # Verifica si el usuario ya le dio 'Me gusta' a este post
    like_exists = Like.objects.filter(post=post, user=request.user).exists()

    if like_exists:
        # Si ya le dio 'Me gusta', lo quita (dislike)
        Like.objects.filter(post=post, user=request.user).delete()
        messages.info(request, f"Ya no te gusta '{post.titulo}'.")
    else:
        # Si no le dio 'Me gusta', lo añade (like)
        Like.objects.create(post=post, user=request.user)
        messages.success(request, f"¡Te gusta '{post.titulo}'!")

    # Redirige de vuelta a la página de detalles del post (o de donde vino)
    # Alternativamente, puedes redirigir a 'post_list' o la URL que desees
    next_url = request.META.get('HTTP_REFERER') # Intenta volver a la página anterior
    if next_url:
        return redirect(next_url)
    return redirect('post_detail', pk=pk) # Redirige a la página de detalles del post como fallback



# Vista para añadir un comentario (usaremos una función simple por ahora)
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.contrib.auth.decorators import login_required
# import json

# @login_required # Solo usuarios logueados pueden comentar
# @require_POST # Solo acepta peticiones POST
# def add_comment(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     data = json.loads(request.body)
#     content = data.get('content')

#     if content:
#         Comentario.objects.create(post=post, autor=request.user, contenido=content)
#         messages.success(request, '¡Tu comentario ha sido añadido!')
#         return JsonResponse({'status': 'success'})
#     return JsonResponse({'status': 'error', 'message': 'El contenido del comentario no puede estar vacío.'}, status=400)


def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # 1. Seguridad: Asegurarse de que el usuario esté autenticado
    if not request.user.is_authenticated:
        messages.warning(request, "Necesitas iniciar sesión para dejar un comentario.")
        return redirect('login') # Redirige al login

    # 2. Verificar que la petición sea POST (un envío de formulario)
    if request.method == 'POST':
        # Instancia el formulario con los datos recibidos de request.POST
        # Y NO json.loads(request.body)
        form = ComentarioForm(request.POST)

        if form.is_valid():
            # No guardamos directamente, commit=False para asignar el post y autor
            comment = form.save(commit=False)
            comment.post = post
            comment.autor = request.user # Asigna el usuario autenticado como autor
            comment.save() # Ahora sí guarda el comentario completo
            messages.success(request, '¡Tu comentario ha sido publicado!')
            return redirect('post_detail', pk=post.pk) # Redirige de vuelta a la página del post
        else:
            # Si el formulario no es válido, agrega un mensaje de error
            messages.error(request, 'Hubo un error al enviar tu comentario. Por favor, revisa los campos.')
            # Es importante redirigir al post_detail para mostrar los mensajes.
            # Idealmente, deberías renderizar la página de detalle con el formulario inválido
            # para que los errores de validación del formulario se muestren al usuario.
            # Para que esto funcione, post_detail.html debe ser capaz de recibir un `comment_form`
            # con errores.
            # Si tu `PostDetailView` es una Class-Based View, necesitarás sobrescribir su `get_context_data`
            # para pasar el formulario, o hacer una lógica más compleja de redirección con parámetros.
            # Por ahora, simplemente redirigimos y confiamos en los mensajes flash.
            return redirect('post_detail', pk=post.pk)
    else: # Si la petición es GET a /post/<pk>/comment/, redirigimos al detalle del post
        return redirect('post_detail', pk=post.pk)    

# Vista para editar comentarios
class ComentarioUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comentario
    form_class = ComentarioForm
    template_name = 'blog/comentario_edit.html'
    context_object_name = 'comentario'
    
    def get_success_url(self):
        # Redirige de vuelta al post después de editar
        return reverse('post_detail', kwargs={'pk': self.object.post.pk})
    
    def test_func(self):
        # Solo permite editar al autor del comentario o al admin
        comentario = self.get_object()
        return self.request.user == comentario.autor or self.request.user.is_superuser
    
    def form_valid(self, form):
        messages.success(self.request, '¡Comentario actualizado exitosamente!')
        return super().form_valid(form)

# Vista para eliminar comentarios
class ComentarioDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comentario
    template_name = 'blog/comentario_confirm_delete.html'
    context_object_name = 'comentario'
    
    def get_success_url(self):
        # Redirige de vuelta al post después de eliminar
        return reverse('post_detail', kwargs={'pk': self.object.post.pk})
    
    def test_func(self):
        # Solo permite eliminar al autor del comentario o al admin
        comentario = self.get_object()
        return self.request.user == comentario.autor or self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '¡Comentario eliminado exitosamente!')
        return super().delete(request, *args, **kwargs)

# Vista para mostrar posts por categoría
class CategoryDetailView(ListView):
    model = Post
    template_name = 'blog/category_detail.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        self.categoria = get_object_or_404(Categoria, pk=self.kwargs['pk'])
        return Post.objects.filter(categoria=self.categoria).order_by('-fecha_publicacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = self.categoria
        context['total_posts'] = self.get_queryset().count()
        return context

# Create your views here.

