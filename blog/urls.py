# blog/urls.py
from django.urls import path
from .views import (
    PostListView, PostDetailView, PostCreateView,
    PostUpdateView, PostDeleteView, RegisterView, add_comment, about_view, contact_view, donations_view, CategoryOverviewView, CategoryDetailView, like_post, ComentarioUpdateView, ComentarioDeleteView
)
from django.contrib.auth import views as auth_views # Vistas de autenticación de Django

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/nuevo/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/editar/', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/eliminar/', PostDeleteView.as_view(), name='post_delete'),
    path('post/<int:pk>/comentar/', add_comment, name='add_comment_to_post'), # Nueva URL para comentarios
    path('acerca-de/', about_view, name='about'), # Nueva URL para acerca de
    path('contacto/', contact_view, name='contact'),
    path('donaciones/', donations_view, name= 'donations'),
    path('categorias/', CategoryOverviewView.as_view(), name='category_overview'), # ¡Esta será la nueva página de inicio!
    path('categoria/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'), # Nueva URL para categorías específicas
    path('post/<int:pk>/like/', like_post, name='like_post'),
    path('comentario/<int:pk>/editar/', ComentarioUpdateView.as_view(), name='comentario_edit'),
    path('comentario/<int:pk>/eliminar/', ComentarioDeleteView.as_view(), name='comentario_delete'),

    # URLs de autenticación de Django
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    # URLs de restablecimiento de contraseña (NUEVAS)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]