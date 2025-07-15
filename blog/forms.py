from django import forms
from .models import Comentario
from django.contrib.auth.forms import UserCreationForm # Importa UserCreationForm
from django.contrib.auth.models import User # Importa el modelo User

class ContactForm(forms.Form):
    """
    Formulario de contacto para que los visitantes puedan enviar mensajes.
    """
    nombre = forms.CharField(max_length=100, label="Tu Nombre")
    correo = forms.EmailField(label="Tu Correo Electrónico")
    asunto = forms.CharField(max_length=200, label="Asunto del Mensaje")
    mensaje = forms.CharField(widget=forms.Textarea, label="Tu Mensaje")
    
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido'] # Esto coincide con el 'name="content"' de tu textarea en post_detail.html
        labels = {
            'contenido': 'Tu Comentario',
        }
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe tu comentario aquí...', 'required': True}),
        }
        
# Nuevo formulario de registro personalizado
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")

    class Meta(UserCreationForm.Meta):
        model = User
        # Asegúrate de incluir 'email' en los campos que se mostrarán
        fields = UserCreationForm.Meta.fields + ('email',) # AÑADE 'email' AQUI

    def clean_email(self):
        email = self.cleaned_data['email']
        # Opcional: Asegurarse de que el correo no esté ya en uso
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email        