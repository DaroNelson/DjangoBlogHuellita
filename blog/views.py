# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Categoria, Comentario
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm # Para el registro
from django.contrib import messages # Para mostrar mensajes al usuario
from django.core.mail import send_mail # Importar para enviar correos
from django.conf import settings # Importar para acceder a settings como EMAIL_HOST_USER

from .forms import ContactForm # Impor formulario de contacto
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

    def test_func(self): # Solo permite al autor del post editarlo
        post = self.get_object()
        return self.request.user == post.autor
    
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
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login') # Redirige a la página de login después del registro

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

