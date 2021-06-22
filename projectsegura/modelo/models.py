from django.db import models

# Create your models here.
class intentos_por_ip(models.Model):
    ip = models.GenericIPAddressField(primary_key=True)
    contador = models.IntegerField(default=0)
    ultima_peticion= models.DateTimeField()

class usuarios(models.Model):
    nombre = models.CharField(max_length=60)
    usuario = models.CharField(max_length=30)
    contra = models.CharField(max_length=100)
    correo = models.EmailField()
    codigo = models.CharField(max_length=10, null=True)
    duracion = models.DateTimeField(null=True)
    salt = models.CharField(max_length=30, null=True)