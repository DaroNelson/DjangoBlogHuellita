# blog/urls.py
from django.urls import path
from .views import (
    PostListView, PostDetailView, PostCreateView,
    PostUpdateView, PostDeleteView, RegisterView, add_comment, about_view, contact_view, donations_view
)
from django.contrib.auth import views as auth_views # Vistas de autenticación de Django

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/nuevo/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/editar/', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/eliminar/', PostDeleteView.as_view(), name='post_delete'),
    path('post/<int:pk>/comentar/', add_comment, name='add_comment'), # Nueva URL para comentarios
    path('acerca-de/', about_view, name='about'), # Nueva URL para acerca de
    path('contacto/', contact_view, name='contact'),
    path('donaciones/', donations_view, name= 'donations'),

    # URLs de autenticación de Django
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]