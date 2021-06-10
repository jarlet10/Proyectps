from django.http import HttpResponse
from django.template import Template,Context
from django.shortcuts import render,redirect
import os
from modelo import models
import base64

from pathlib import Path

#----------------------------------------------------------------
def registrar_usuario(request):
    if request.method == 'GET':
        t = 'registrar.html'
        return render(request,t)
    elif request.method == 'POST':
        t = 'registrar.html'
        return render(request,t)

#----------------------------------------------------------------
def iniciar_sesion(request):
    if request.method == 'GET':
        t = 'iniciar_sesion.html'
        return render(request,t)
    elif request.method == 'POST':
        t = 'registrar.html'
        return render(request,t)

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
