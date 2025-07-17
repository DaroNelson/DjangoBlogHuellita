# Huellitas - Un Blog de Noticias en Django

## Descripción del Proyecto

**Huellitas** es un blog de noticias desarrollado con Django, diseñado para publicar y gestionar artículos de forma dinámica. Ofrece funcionalidades esenciales para un blog moderno, permitiendo a los usuarios autenticarse, comentar publicaciones, dar "Me gusta", y explorar contenido por categorías. El proyecto está construido con una interfaz de usuario limpia y responsiva, utilizando Bootstrap 5 y Crispy Forms para una mejor experiencia.

## Características Principales

* **Gestión de Posts:**
    * Creación, edición y eliminación de publicaciones (solo usuarios autenticados, con permisos de autor o superusuario).
    * Asignación de categorías a los posts.
    * Inclusión de imágenes de portada para los posts.
* **Comentarios:**
    * Usuarios autenticados pueden dejar comentarios en los posts.
    * Edición y eliminación de comentarios (solo por el autor del comentario o superusuario).
* **Sistema de "Me Gusta":**
    * Usuarios autenticados pueden dar "Me gusta" a los posts.
    * Muestra el conteo total de "Me gusta" por post.
    * Manejo visual del botón "Me gusta"/"Ya no me gusta" dinámicamente.
* **Categorías:**
    * Posts organizados por categorías.
    * Página de "Explorar Categorías" que muestra un resumen de las categorías y los últimos posts en cada una.
    * Filtrado de posts por categoría en la lista principal de posts, opcion de orden asc y desc por fecha de publicacion y titulo.
* **Autenticación y Autorización:**
    * Registro de nuevos usuarios con formulario personalizado (incluye correo electrónico).
    * Inicio y cierre de sesión.
    * Restablecimiento de contraseña.
    * Control de acceso basado en roles para la creación, edición y eliminación de posts y comentarios.
* **Paginación:**
    * Paginación de posts en la vista principal para una mejor navegación.
* **Páginas Informativas:**
    * "Acerca de".
    * "Contacto" con formulario funcional para enviar mensajes por correo electrónico.
    * "Donaciones" (con enlace directo a whatsapp para compartir datos de cuenta para donaciones).
* **Diseño Responsivo:**
    * Implementado con Bootstrap 5 para una experiencia consistente en diferentes dispositivos.
    * Modo Oscuro/Claro (Dark/Light Mode) con persistencia de preferencia en `localStorage`.

## Estructura del Proyecto

El proyecto sigue una estructura típica de Django:
mi_blog_noticias/
├── mi_blog_noticias/       # Directorio principal del proyecto (configuración global)
│   ├── init.py
│   ├── settings.py         # Configuración del proyecto
│   ├── urls.py             # URLs principales del proyecto
│   └── wsgi.py
├── blog/                   # Aplicación principal del blog
│   ├── migrations/
│   ├── static/             # Archivos estáticos de la app (CSS, JS, imágenes)
│   │   └── css/
│   │       └── styles.css
│   ├── templates/
│   │   └── blog/           # Plantillas HTML de la aplicación blog
│   │       ├── base.html
│   │       ├── post_list.html
│   │       ├── post_detail.html
│   │       ├── post_form.html
│   │       ├── post_confirm_delete.html
│   │       ├── category_overview.html
│   │       ├── category_detail.html
│   │       ├── comentario_confirm_delete.html
│   │       ├── about.html
│   │       ├── contact.html
│   │       └── donations.html
│   │   └── registration/   # Plantillas para autenticación (login, registro, password reset)
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── password_reset_form.html
│   │       ├── password_reset_done.html
│   │       └── password_reset_confirm.html
│   ├── init.py
│   ├── admin.py            # Registro de modelos en el panel de administración
│   ├── apps.py
│   ├── context_processors.py # Para pasar datos globales a las plantillas
│   ├── forms.py            # Definición de formularios
│   ├── models.py           # Modelos de base de datos
│   ├── urls.py             # URLs de la aplicación blog
│   └── views.py            # Lógica de las vistas
├── media/                  # Almacena los archivos subidos por los usuarios (ej. imágenes de posts)
├── db.sqlite3              # Base de datos SQLite (para desarrollo)
└── manage.py               # Utilidad de línea de comandos de Django

## Modelos de Base de Datos (blog/models.py)

El esquema de la base de datos se compone de los siguientes modelos:

### 1. `Categoria`
* **Propósito:** Organizar los posts por temas.
* **Campos:**
    * `nombre`: `CharField` (max\_length=100, `unique=True`) - Nombre único de la categoría.
    * `descripcion`: `TextField` (opcional) - Descripción breve de la categoría.

### 2. `Post`
* **Propósito:** Representa cada artículo o publicación del blog.
* **Relaciones:**
    * `autor`: `ForeignKey` a `User` (relación Uno a Muchos) - El usuario que creó el post. Si el usuario es eliminado, sus posts también.
    * `categoria`: `ForeignKey` a `Categoria` (relación Uno a Muchos, opcional) - La categoría a la que pertenece el post. Si la categoría se elimina, el campo se pone a `NULL`.
* **Campos:**
    * `titulo`: `CharField` (max\_length=200) - Título del post.
    * `contenido`: `TextField` - Contenido completo del post.
    * `fecha_publicacion`: `DateTimeField` (auto\_now\_add=True) - Fecha y hora de creación del post.
    * `imagen_portada`: `ImageField` (opcional) - Imagen destacada para el post.
    * `total_likes`: `@property` que devuelve la cantidad de "Me gusta" que tiene el post.

### 3. `Comentario`
* **Propósito:** Almacena los comentarios realizados en los posts.
* **Relaciones:**
    * `post`: `ForeignKey` a `Post` (relación Uno a Muchos) - El post al que pertenece el comentario. Si el post se elimina, el comentario también.
    * `autor`: `ForeignKey` a `User` (relación Uno a Muchos) - El usuario que escribió el comentario.
* **Campos:**
    * `contenido`: `TextField` - Texto del comentario.
    * `fecha_creacion`: `DateTimeField` (auto\_now\_add=True) - Fecha y hora de creación del comentario.

### 4. `Like`
* **Propósito:** Registra los "Me gusta" que los usuarios dan a los posts.
* **Relaciones:**
    * `user`: `ForeignKey` a `User` (relación Uno a Muchos) - El usuario que dio "Me gusta".
    * `post`: `ForeignKey` a `Post` (relación Uno a Muchos) - El post al que se le dio "Me gusta".
* **Restricciones:**
    * `unique_together = ('user', 'post')` - Asegura que un usuario solo pueda dar "Me gusta" a un post una única vez.

## Vistas (blog/views.py)

Las vistas implementan la lógica de negocio y manejan las solicitudes HTTP.

* `PostListView`: Lista todos los posts, con paginación (5 posts por página), y soporte para filtros por categoría, fecha, si tienen comentarios, y ordenación (por antigüedad, título).
* `PostDetailView`: Muestra el detalle de un post específico. Pasa al contexto el `ComentarioForm` y una variable `user_has_liked` para controlar el estado del botón "Me gusta".
* `PostCreateView`: Permite a los usuarios autenticados crear nuevos posts. Asigna automáticamente el autor del post al usuario logueado.
* `PostUpdateView`: Permite al autor del post o a un superusuario editar un post existente.
* `PostDeleteView`: Permite al autor del post o a un superusuario eliminar un post.
* `RegisterView`: Maneja el registro de nuevos usuarios utilizando `CustomUserCreationForm`.
* `add_comment`: Función para añadir un comentario a un post (requiere autenticación).
* `like_post`: Función para añadir o quitar un "Me gusta" a un post.
* `ComentarioUpdateView`: Permite al autor del comentario o a un superusuario editar un comentario existente.
* `ComentarioDeleteView`: Permite al autor del comentario o a un superusuario eliminar un comentario.
* `about_view`: Vista simple para la página "Acerca de".
* `contact_view`: Maneja el formulario de contacto y envía correos electrónicos.
* `donations_view`: Vista simple para la página "Donaciones".
* `CategoryOverviewView`: Muestra una página con todas las categorías y los últimos posts de cada una.
* `CategoryDetailView`: Muestra una lista de posts filtrados por una categoría específica.

## Formularios (blog/forms.py)

* `ContactForm`: Formulario para que los visitantes puedan enviar mensajes a través de la página de contacto. Incluye campos para nombre, correo, asunto y mensaje.
* `ComentarioForm`: Formulario para que los usuarios autenticados puedan añadir comentarios a los posts. Solo incluye el campo `contenido`.
* `CustomUserCreationForm`: Formulario personalizado de creación de usuario que extiende `UserCreationForm` de Django y añade un campo para el correo electrónico, haciéndolo requerido.

## Archivos de URLs

### `mi_blog_noticias/urls.py` (URL's principales del proyecto)
Este archivo enruta las solicitudes a la aplicación `blog` y maneja las URLs de administración y autenticación de Django.

```python
# Contenido general de mi_blog_noticias/urls.py (Ejemplo, el tuyo puede variar ligeramente)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')), # Incluye las URLs de la aplicación 'blog'
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

blog/urls.py (URL's de la aplicación blog)
Este archivo define las rutas específicas para la aplicación blog, incluyendo posts, comentarios, categorías y autenticación.

Algunas de las rutas clave incluyen:

/: Lista de posts (post_list).

/post/<int:pk>/: Detalle de un post (post_detail).

/post/nuevo/: Crear nuevo post (post_create).

/post/<int:pk>/editar/: Editar post (post_update).

/post/<int:pk>/eliminar/: Eliminar post (post_delete).

/post/<int:pk>/comentar/: Añadir comentario (add_comment_to_post).

/comentario/<int:pk>/editar/: Editar comentario (comentario_edit).

/comentario/<int:pk>/eliminar/: Eliminar comentario (comentario_delete).

/post/<int:pk>/like/: Dar/quitar "Me gusta" (like_post).

/acerca-de/: Página "Acerca de" (about).

/contacto/: Página de contacto (contact).

/donaciones/: Página de donaciones (donations).

/categorias/: Resumen de categorías (category_overview).

/categoria/<int:pk>/: Posts por categoría (category_detail).

/login/: Inicio de sesión.

/logout/: Cierre de sesión.

/register/: Registro de usuario.

URLs para restablecimiento de contraseña (password_reset, password_reset_done, password_reset_confirm, password_reset_complete).

Herramientas y Tecnologías
Django 5.2.4: Framework web de Python.

Python: Lenguaje de programación principal.

SQLite3: Base de datos utilizada en entorno de desarrollo.

Bootstrap 5: Framework CSS para el diseño responsivo.

Crispy Forms & Crispy Bootstrap5: Para un renderizado de formularios más limpio y sencillo.

Pillow: Librería para el manejo de imágenes (requerida para ImageField).

Font Awesome & Bootstrap Icons: Para iconos.

Google Fonts: Fuentes personalizadas para la tipografía.

Configuración y Entorno de Desarrollo
Requisitos
Python 3.x

pip (gestor de paquetes de Python)

Pasos de Instalación y Ejecución
Clonar el repositorio:

Bash

git clone <URL_DE_TU_REPOSITORIO>
cd mi_blog_noticias
Crear y activar un entorno virtual:
Es una buena práctica aislar las dependencias del proyecto.

Bash

python -m venv venv
# En Windows:
.\venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
Instalar las dependencias:
Crea un archivo requirements.txt con todas tus dependencias (ej. Django, Pillow, django-crispy-forms, crispy-bootstrap5).

Bash

pip install -r requirements.txt
Si no tienes un requirements.txt, puedes instalarlas manualmente:

Bash

pip install Django pillow django-crispy-forms crispy-bootstrap5
Realizar migraciones de base de datos:
Esto creará las tablas de la base de datos definidas por tus modelos.

Bash

python manage.py makemigrations blog
python manage.py migrate
Crear un superusuario (administrador):
Necesitarás un superusuario para acceder al panel de administración de Django y crear contenido.

Bash

python manage.py createsuperuser
Sigue las instrucciones en pantalla para establecer un nombre de usuario, correo electrónico y contraseña.

Configurar el correo electrónico para el formulario de contacto (opcional):
En mi_blog_noticias/settings.py, descomenta y configura las variables EMAIL_BACKEND, EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, y DEFAULT_FROM_EMAIL con tus credenciales SMTP (por ejemplo, de Gmail). Si usas Gmail, recuerda generar una "contraseña de aplicación" en tu cuenta de Google.

Ejecutar el servidor de desarrollo:

Bash

python manage.py runserver
El blog estará disponible en http://127.0.0.1:8000/.
