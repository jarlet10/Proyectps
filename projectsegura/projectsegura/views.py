from django.http import HttpResponse
from django.template import Template,Context
from django.shortcuts import render,redirect
import os
from modelo import models
import base64

from pathlib import Path

#----------------------------------------------------------------
def nombre_exite(usuario1): #comprobar si el usuario esta repetido
    usuarioRepetido = models.usuarios.objects.filter(nombre=usuario1.nombre)
    if len(usuarioRepetido) > 0:
        return True
    return False

def usuario_exite(usuario1): #comprobar si el usuario esta repetido
    usuarioRepetido = models.usuarios.objects.filter(usuario=usuario1.usuario)
    if len(usuarioRepetido) > 0:
        return True
    return False

def tiene_errores_usuario(usuario1,contrac):#recolectar errores
    errores = []  
    if nombre_exite(usuario1):
        errores.append('El Usuario %s ya existe' % usuario1.nombre)
    if usuario_exite(usuario1):
        errores.append('El Usuario %s ya existe' % usuario1.usuario)
    if usuario1.nombre == '':
        errores.append('Nombre vacio')
    if usuario1.usuario == '':
        errores.append('Usuario vacio')
    if usuario1.correo == '':
        errores.append('Correo vacio')
    if usuario1.contra == '':
        errores.append('Contraseña vacia')
    if usuario1.contra != contrac:
        errores.append('Las contraseñas no coinciden')
    return errores

def registrar_usuario(request):
    if request.method == 'GET':
        t = 'registrar.html'
        return render(request,t)
    elif request.method == 'POST':
        t = 'registrar.html'

        nombre = request.POST.get('nombre','').strip()
        print(nombre)
        usuario = request.POST.get('nick','').strip()
        correo = request.POST.get('correo','').strip()
        contra = request.POST.get('contra','').strip()
        contrac = request.POST.get('contrac','').strip()

        usuariox = models.usuarios()
        usuariox.nombre = nombre
        usuariox.usuario = usuario
        usuariox.correo = correo
        usuariox.contra = contra

        errores = tiene_errores_usuario(usuariox, contrac)
        
        print(errores)

        if not errores:
            usuariox.save() #gurdar usuario en base de datos
            return redirect('/iniciar_sesion')
        else:
            c = {'errores': errores, 'usuario': usuariox}
            return render(request,t,c)

#----------------------------------------------------------------
def iniciar_sesion(request):
    if request.method == 'GET':
        t = 'iniciar_sesion.html'
        return render(request,t)
    elif request.method == 'POST':
        usuariob = request.POST.get('usuario','').strip()
        contra = request.POST.get('password','').strip()
        try:
            models.usuarios.objects.get(usuario=usuariob,contra=contra)
            return redirect('/ver_listado')
        except:
            t = 'iniciar_sesion.html'
            errores = ['usuario o contraseña invalidos']
            c = {'errores': errores, 'usuario': usuariob, 'contra': contra}
            return render(request,t,c)

#----------------------------------------------------------------
def registrar_credencial(request):
    if request.method == 'GET':
        t = 'registrarcredencial.html'
        return render(request,t)
    elif request.method == 'POST':
        t = 'registrar.html'
        return render(request,t)

#-----------------------------------------------------------------
def ver_detalles_credencial(request):
    if request.method == 'GET':
        t = 'verdetallescredencial.html'
        return render(request,t)
    elif request.method == 'POST':
        t = 'registrar.html'
        return render(request,t)

#----------------------------------------------------------------
def editar_credencial(request):
    if request.method == 'GET':
        t = 'editarcredencial.html'
        return render(request,t)
    elif request.method == 'POST':
        t = 'registrar.html'
        return render(request,t)

#----------------------------------------------------------------
def ver_listado_cuentas(request):
    if request.method == 'GET':
        t = 'verlistado.html'
        return render(request,t)
    elif request.method == 'POST':
        t = 'registrar.html'
        return render(request,t)

#----------------------------------------------------------------
def compartir(request):
    if request.method == 'GET':
        t = 'compartir.html'
        return render(request,t)
    elif request.method == 'POST':
        t = 'registrar.html'
        return render(request,t)
