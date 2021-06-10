from django.db import models

# Create your models here.

class usuarios(models.Model):
    nombre = models.CharField(max_length=60)
    usuario = models.CharField(max_length=30)
    contra = models.CharField(max_length=40)
    correo = models.EmailField()