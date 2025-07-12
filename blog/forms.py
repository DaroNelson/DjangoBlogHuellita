from django import forms
from .models import Comentario

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