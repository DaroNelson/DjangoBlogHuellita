from django import forms

class ContactForm(forms.Form):
    """
    Formulario de contacto para que los visitantes puedan enviar mensajes.
    """
    nombre = forms.CharField(max_length=100, label="Tu Nombre")
    correo = forms.EmailField(label="Tu Correo Electrónico")
    asunto = forms.CharField(max_length=200, label="Asunto del Mensaje")
    mensaje = forms.CharField(widget=forms.Textarea, label="Tu Mensaje")