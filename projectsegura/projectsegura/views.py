from django.http import HttpResponse
from django.template import Template,Context
from django.shortcuts import render,redirect
import os
from modelo import models
import base64
import datetime
from datetime import timezone
from pathlib import Path
from projectsegura.decoradores import login_requerido
from projectsegura.passHash import cif, des
from projectsegura.cifradoSimetrico import cifrar, descifrar, generar_llave_aes_from_password
import re

#----------------------------------------------------------------------------
#Para enviar mensaje a telegram bot
import requests
    
def mandar_mensaje_bot_post(mensaje):
    #token = os.environ.get('token')
    #chat_id = os.environ.get('chat_id')
    token = '1862504006:AAEr91Gc0keP4lJkNE59qwK3wAMXrz1CLqU'
    chat_id = '678557081'
    datos = {'chat_id': chat_id, 'text': mensaje}
    url = 'https://api.telegram.org/bot'+ token +'/sendMessage'
    response = requests.post(url = url, data = datos)

#----------------------------------------------------------------

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def diferencia_tiempo(tiempoPasado):
    ahora = datetime.datetime.now(timezone.utc)
    diferencia = ahora - tiempoPasado
    return diferencia.seconds

#Intentaer 3 intentos por menos de 1 mnuto te bloquea
def puede_intentar(ip):
    """ Determina si una ip puede volver a intentar enviar el formulario
        3 intentos maximo por minutos
        tiene efectos en la base de datos
    """
    #Primer caso la ip es nueva
    registro_guardado = models.intentos_por_ip.objects.filter(pk=ip)
    if not registro_guardado: #si no hay registros guardamos
        registro = models.intentos_por_ip(ip=ip, contador=1, ultima_peticion=datetime.datetime.now(timezone.utc))
        registro.save()
        return True
    registro_guardado = registro_guardado[0]
    diferencia_tiempo_segundos = diferencia_tiempo(registro_guardado.ultima_peticion)
    if diferencia_tiempo_segundos >= 60: #debemos resetear
        registro_guardado.ultima_peticion = datetime.datetime.now(timezone.utc)
        registro_guardado.contador = 1
        registro_guardado.save()
        return True
    else:
        if registro_guardado.contador < 3:
            registro_guardado.ultima_peticion = datetime.datetime.now(timezone.utc)
            registro_guardado.contador += 1
            registro_guardado.save()
            return True
        else:
            registro_guardado.ultima_peticion = datetime.datetime.now(timezone.utc)
            return False


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

def tiene_errores_usuario(usuario1,contrac):#recolectar errores jars aqui ves lo de expreciones regulares en python
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
    if not re.match('^(?=(?:.*\d))(?=.*[A-Z])(?=.*[a-z])(?=.*[.,*!?@¿¡/#$%&])\S{8,20}$', usuario1.contra):
        errores.append('La contrasena debe cumplir las politicas')
    return errores

def tiene_errores_credencial(credencial1):#recolectar errores jars aqui ves lo de expreciones regulares en python
    errores = []  
    if credencial1.nombre_cuenta == '':
        errores.append('Nombre de cuenta vacio')
    if credencial1.usuario_cuenta == '':
        errores.append('Usuario de cuenta vacio')
    if credencial1.contra_cuenta == '':
        errores.append('Contraseña vacia')
    if credencial1.url == '':
        errores.append('Url vacia')
    return errores

def registrar_usuario(request):
    if request.method == 'GET':
        t = 'registrar.html'
        logueado = request.session.get('logueado', False) #redireccionar si ya estas logueado
        if logueado:
            return redirect('/ver_listado')
        return render(request,t)
    elif request.method == 'POST':
        t = 'registrar.html'

        nombre = request.POST.get('nombre','').strip()
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

        if not errores:
            salt = os.urandom(16)
            usuariox.contra = cif(contra, salt)
            salt = base64.b64encode(salt).decode('utf-8')
            print(salt)
            print(usuariox.contra)
            usuariox.salt = salt
            usuariox.save() #gurdar usuario en base de datos
            request.session['logueado'] = False
            return redirect('/iniciar_sesion')
        else:
            c = {'errores': errores, 'usuario': usuariox}
            return render(request,t,c)

""" def iniciar_sesion2(request):
    if request.method == 'GET':
        t = 'inicar.html'
        return render(request,t)
    elif request.method == 'POST':
        if request.POST.get("form_type") == 'formOne':
            return HttpResponse('Hola1')
        elif request.POST.get("form_type") == 'formTwo':
            return HttpResponse('Hola2') """

#----------------------------------------------------------------

def iniciar_sesion(request):
    if request.method == 'GET':
        t = 'iniciar_sesion.html'
        logueado = request.session.get('logueado',False)
        if logueado:
            return redirect('/ver_listado')
        return render(request,t)
    elif request.method == 'POST':
        if request.POST.get("form_type") == 'formUno':
            usuariob = request.POST.get('usuario','').strip()
            contra = request.POST.get('password','').strip()
            ip = get_client_ip(request)
            if puede_intentar(ip):
                try:
                    usuarioc = models.usuarios.objects.get(usuario=usuariob)
                    saltbd = usuarioc.salt
                    salt = base64.b64decode(saltbd)
                    key = usuarioc.contra
                    contrades = des(contra,key,salt) # aqui verificas la contraseña cifrafa
                    if contrades:
                        codigo = base64.b64encode(os.urandom(6)).decode('utf-8')
                        usuariobd = models.usuarios.objects.get(usuario=usuariob)
                        usuariobd.codigo = codigo
                        usuariobd.duracion = datetime.datetime.now(timezone.utc)
                        usuariobd.save()
                        mandar_mensaje_bot_post(codigo)
                        t = 'iniciar_sesion.html'
                        c = {'okay': True, 'usuario': usuariob, 'contra': contra}
                        return render(request,t,c)
                    else:
                        t = 'iniciar_sesion.html'
                        errores = ['usuario o contraseña invalidos']
                        c = {'errores': errores, 'usuario': usuariob, 'contra': contra}
                        return render(request,t,c)
                except:
                    t = 'iniciar_sesion.html'
                    errores = ['usuario o contraseña invalidos']
                    c = {'errores': errores, 'usuario': usuariob, 'contra': contra}
                    return render(request,t,c)
            else:
                t = 'iniciar_sesion.html'
                error = ['Intentos Agotados Por favor Espere 1 minuto']
                c = {'errores': error}
                return render(request,t,c)
        elif request.POST.get("form_type") == 'formDos':
            usuariob = request.POST.get('usuario','').strip()
            contra = request.POST.get('password','').strip()
            codigou = request.POST.get('codigo').strip()
            usuariobd = models.usuarios.objects.get(usuario=usuariob)
            diferencia_tiempo_segundos = diferencia_tiempo(usuariobd.duracion)
            if diferencia_tiempo_segundos <= 180:
                if codigou == usuariobd.codigo:
                    request.session['logueado'] = True
                    request.session['usuario'] = usuariob
                    #respuesta = redirect('/ver_listado')
                    #respuesta.set_cookie('usuario', usuariob, max_age=None, httponly=True, samesite='Strict')
                    return redirect('/ver_listado')
                else:
                    t = 'iniciar_sesion.html'
                    error = ['Error el codigo no era el correcto']
                    c = {'okay':True, 'erroresf2': error, 'usuario': usuariob, 'contra': contra, 'codigo': codigou}
                    return render(request,t,c)
            else:
                usuariobd.duracion = datetime.datetime.now(timezone.utc)
                t = 'iniciar_sesion.html'
                error = ['Intentos Agotados Por favor Espere 3 minuto']
                c = {'errores': error, 'usuario': usuariob, 'contra': contra}
                return render(request,t,c)


@login_requerido
def salir_login(request):
    request.session.flush()
    return redirect('/iniciar_sesion')

#----------------------------------------------------------------
@login_requerido
def registrar_credencial(request):
    if request.method == 'GET':
        t = 'editarcredencial.html'
        return render(request,t)
    elif request.method == 'POST':

        if request.POST.get("form_type") == 'formUno':
            nomCuenta = request.POST.get('nomCuenta','').strip()
            usuarioC = request.POST.get('usuarioC','').strip()
            contrasena = request.POST.get('contrasena','').strip()
            url = request.POST.get('url','').strip()
            detalles = request.POST.get('detalles','').strip()        

            t = 'editarcredencial.html'
            c = {'okay':True, 'nomCuenta': nomCuenta, 'usuarioC': usuarioC, 'contrasena': contrasena, 'url': url, 'detalles': detalles}
            return render(request,t,c)
            
        elif request.POST.get("form_type") == 'formDos':
            nomCuenta = request.POST.get('nomCuenta','').strip()
            usuarioC = request.POST.get('usuarioC','').strip()
            contrasena = request.POST.get('contrasena','').strip()
            url = request.POST.get('url','').strip()
            detalles = request.POST.get('detalles','').strip()
            contram = request.POST.get('contrasenaM','').strip()
            #usuariocookie = request.COOKIES.get('usuario')
            usuariocookie = request.session.get('usuario','').strip()

            try:
                usuariopw = models.usuarios.objects.get(usuario=usuariocookie)
                saltbd = usuariopw.salt
                salt = base64.b64decode(saltbd)
                key = usuariopw.contra
                contrades = des(contram,key,salt) # aqui verificas la contraseña cifrafa
                
                if contrades:
                    credencialx = models.credenciales()
                    credencialx.nombre_cuenta = nomCuenta
                    credencialx.usuario_cuenta = usuarioC
                    credencialx.contra_cuenta = contrasena
                    credencialx.url = url
                    credencialx.detalles = detalles
                    credencialx.usuario_asociado = usuariopw

                    errores = tiene_errores_credencial(credencialx)
                    

                    if not errores:
                        iv = os.urandom(16)
                        contracif = cifrar(contrasena,contram,iv)
                        contracif = base64.b64encode(contracif).decode('utf-8')        
                        credencialx.contra_cuenta = contracif
                        iv = base64.b64encode(iv).decode('utf-8')
                        credencialx.iv = iv
                        credencialx.save()
                        return redirect('/ver_listado')

                    else:
                        t = 'editarcredencial.html'
                        c = {'errores': errores, 'nomCuenta': nomCuenta, 'usuarioC': usuarioC, 'contrasena': contrasena, 'url': url, 'detalles': detalles}
                        return render(request,t,c)
                else:
                    t = 'editarcredencial.html'
                    errores = ['Contraseña invalida']
                    c = {'okay': True,'erroresf2': errores, 'nomCuenta': nomCuenta, 'usuarioC': usuarioC, 'contrasena': contrasena, 'url': url, 'detalles': detalles, 'contrasenaM': contram}
                    return render(request,t,c)
                      
            except:
                 t = 'editarcredencial.html'
                 errores = ['Ocurrio un error, porfavor comunicate con el administrador']
                 c = {'errores': errores, 'nomCuenta': nomCuenta, 'usuarioC': usuarioC, 'contrasena': contrasena, 'url': url, 'detalles': detalles, 'contrasenaM': contram}
                 return render(request,t,c)


#-----------------------------------------------------------------
@login_requerido
def ver_listado_cuentas(request):
    if request.method == 'GET':
        t = 'verlistado.html'
        usuariocookie = request.session.get('usuario','').strip()
        usuariopw = models.usuarios.objects.get(usuario=usuariocookie)
        pk = usuariopw.id
        credencialesx = models.credenciales.objects.all().filter(usuario_asociado=pk)
        c = {'credencialesx': credencialesx}
        return render(request,t,c)
    elif request.method == 'POST':
        
        if request.POST.get("form_type") == 'formUno':
            t = 'verlistado.html'
            credencialesx = models.credenciales.objects.all()
            c = {'credencialesx': credencialesx}
            return render(request,t,c)

        if request.POST.get("form_type") == 'formDos':
            t = 'verlistado.html'
            nombreCuenta = request.POST.get('nombreCuenta','').strip()
            usuarioCuenta = request.POST.get('usuarioCuenta','').strip()
            request.session['logueadov'] = True
            request.session['nombreC'] = nombreCuenta
            request.session['usC'] = usuarioCuenta
            

            return redirect('/ver_detalles_credencial')

        elif request.POST.get("form_type") == 'formTres':
            nombreCuenta = request.POST.get('nombreCuenta','').strip()
            usuarioCuenta = request.POST.get('usuarioCuenta','').strip()
            request.session['logueadoe'] = True
            request.session['nombreC'] = nombreCuenta
            request.session['usC'] = usuarioCuenta
            
            return redirect('/editar_credencial')

#----------------------------------------------------------------
@login_requerido
def editar_cuenta(request):
    if request.method == 'GET':
        t = 'editarcredencial.html'
        logueadoe = request.session.get('logueadoe',False)
        if not logueadoe:
            return redirect('/ver_listado')
    
        nombreCuenta = request.session.get('nombreC','').strip()
        usuarioCuenta = request.session.get('usC','').strip()
        try:

            credencial = models.credenciales.objects.get(nombre_cuenta=nombreCuenta, usuario_cuenta=usuarioCuenta)
            c = {'credencial': credencial, 'nombreCuenta': nombreCuenta}
            return render(request,t,c)
            
        except:
           errores =['Ocurrio un error comunicate con el administrador']
           c = {'errores': errores}
           return render(request,t,c)

    elif request.method == 'POST':
        nombreCuenta = request.session.get('nombreC','').strip()
        usuarioCuenta = request.session.get('usC','').strip()
        if request.POST.get("form_type") == 'formUno':        
            nomCuenta = request.POST.get('nomCuenta','').strip()
            usuarioC = request.POST.get('usuarioC','').strip()
            contrasena = request.POST.get('contrasena','').strip()
            url = request.POST.get('url','').strip()
            detalles = request.POST.get('detalles','').strip()

            try:

                credencial = models.credenciales.objects.get(nombre_cuenta=nombreCuenta, usuario_cuenta=usuarioCuenta)

                credencialx = models.credenciales()
                credencialx.nombre_cuenta = nomCuenta
                credencialx.usuario_cuenta = usuarioC
                credencialx.contra_cuenta = contrasena
                credencialx.url = url
                
                errores = tiene_errores_credencial(credencialx)
                    

                if not errores:
                    t = 'editarcredencial.html'
                    c = {'okay': True, 'credencial': credencial, 'nomCuenta': nomCuenta, 'usuarioC': usuarioC, 'contrasena': contrasena, 'url': url, 'detalles': detalles}
                    return render(request,t,c)
                else:
                    credencial = models.credenciales.objects.get(nombre_cuenta=nombreCuenta, usuario_cuenta=usuarioCuenta)
                    print(credencial.nombre_cuenta)
                    t = 'editarcredencial.html'
                    c = {'errores': errores, 'credencial': credencial}
                    return render(request,t,c)

            except:
                credencial = models.credenciales.objects.get(nombre_cuenta=nombreCuenta, usuario_cuenta=usuarioCuenta)
                t = 'editarcredencial.html'
                errores = ['Ocurrio un error, porfavor comunicate con el administrador']
                c = {'errores': errores, 'credencial': credencial}
                return render(request,t,c)

        elif request.POST.get("form_type") == 'formDos':
            nomCuenta = request.POST.get('nomCuenta','').strip()
            usuarioC = request.POST.get('usuarioC','').strip()
            contrasena = request.POST.get('contrasena','').strip()
            url = request.POST.get('url','').strip()
            detalles = request.POST.get('detalles','').strip()
            contram = request.POST.get('contrasenaM','').strip()
            usuariocookie = request.session.get('usuario','').strip()

            try:
                usuariopw = models.usuarios.objects.get(usuario=usuariocookie)
                saltbd = usuariopw.salt
                salt = base64.b64decode(saltbd)
                key = usuariopw.contra
                contrades = des(contram,key,salt) # aqui verificas la contraseña cifrafa
                
                if contrades:
                    credencial = models.credenciales.objects.get(nombre_cuenta=nombreCuenta, usuario_cuenta=usuarioCuenta)

                    credencial.nombre_cuenta = nomCuenta
                    credencial.usuario_cuenta = usuarioC
                    credencial.contra_cuenta = contrasena
                    credencial.url = url
                    credencial.detalles = detalles
                    credencial.usuario_asociado = usuariopw

                    errores = tiene_errores_credencial(credencial)
                    

                    if not errores:
                        iv = os.urandom(16)
                        contracif = cifrar(contrasena,contram,iv)
                        contracif = base64.b64encode(contracif).decode('utf-8')        
                        credencial.contra_cuenta = contracif
                        iv = base64.b64encode(iv).decode('utf-8')
                        credencial.iv = iv
                        credencial.save()
                        return redirect('/ver_listado')

                    else:
                        credencial = models.credenciales.objects.get(nombre_cuenta=nombreCuenta, usuario_cuenta=usuarioCuenta)
                        print(credencial.nombre_cuenta)
                        t = 'editarcredencial.html'
                        c = {'errores': errores, 'credencial': credencial}
                        return render(request,t,c)
                else:
                    credencial = models.credenciales.objects.get(nombre_cuenta=nombreCuenta, usuario_cuenta=usuarioCuenta)
                    t = 'editarcredencial.html'
                    errores = ['Contraseña invalida']
                    c = {'okay': True,'erroresf2': errores,'credencial': credencial, 'nomCuenta': nomCuenta, 'usuarioC': usuarioC, 'contrasena': contrasena, 'url': url, 'detalles': detalles}
                    return render(request,t,c)
                      
            except:
                credencial = models.credenciales.objects.get(nombre_cuenta=nombreCuenta, usuario_cuenta=usuarioCuenta)
                t = 'editarcredencial.html'
                errores = ['Ocurrio un error, porfavor comunicate con el administrador']
                c = {'errores': errores, 'credencial': credencial}
                return render(request,t,c)
        

#----------------------------------------------------------------
@login_requerido
def ver_detalles_cuenta(request):
    if request.method == 'GET':
        t = 'verdetallescuenta.html'
        logueadov = request.session.get('logueadov',False)
        if not logueadov:
           return redirect('/ver_listado')

        nombreCuenta = request.session.get('nombreC','').strip()
        usuarioCuenta = request.session.get('usC','').strip()
        usuariocookie = request.session.get('usuario','').strip()
        
        try:
            usuariopw = models.usuarios.objects.get(usuario=usuariocookie)
            pk = usuariopw.id
            credenciales = models.credenciales.objects.all().filter(usuario_asociado=pk).filter(nombre_cuenta=nombreCuenta).filter(usuario_cuenta=usuarioCuenta)
            #print(credencial.nombre_cuenta)
            c = {'contracifrada': True, 'credenciales': credenciales}
            return render(request,t,c)
        except:
           errores =['Ocurrio un error comunicate con el administrador']
           c = {'errores': errores}
           return render(request,t,c)

    elif request.method == 'POST':
        t = 'verdetallescuenta.html'
        usuariocookie = request.session.get('usuario','').strip()
        nombreCuenta = request.session.get('nombreC','').strip()
        usuarioCuenta = request.session.get('usC','').strip()

        if request.POST.get("form_type") == 'formUno':
            try:
                usuariopw = models.usuarios.objects.get(usuario=usuariocookie)
                pk = usuariopw.id
                credenciales = models.credenciales.objects.all().filter(usuario_asociado=pk).filter(nombre_cuenta=nombreCuenta).filter(usuario_cuenta=usuarioCuenta)
                #print(credencial.nombre_cuenta)
                c = {'okay': True,'contracifrada': True,'credenciales': credenciales}
                return render(request,t,c)
            except:
                errores =['Ocurrio un error comunicate con el administrador']
                c = {'errores': errores}
                return render(request,t,c)
            
        elif request.POST.get("form_type") == 'formDos':
            contram = request.POST.get('contrasenaM','').strip()
            usuariopw = models.usuarios.objects.get(usuario=usuariocookie)
            saltbd = usuariopw.salt
            salt = base64.b64decode(saltbd)
            key = usuariopw.contra
            contrades = des(contram,key,salt) # aqui verificas la contraseña cifrafa
                
            if contrades:
                try:
                    pk = usuariopw.id
                    credenciales = models.credenciales.objects.all().filter(usuario_asociado=pk).filter(nombre_cuenta=nombreCuenta).filter(usuario_cuenta=usuarioCuenta)
                    usuariopw = models.usuarios.objects.get(usuario=usuariocookie)
                    credencial = models.credenciales.objects.get(nombre_cuenta=nombreCuenta, usuario_cuenta=usuarioCuenta)
                    contracifrada = credencial.contra_cuenta
                    iv = credencial.iv
                    #contracifrada = base64.b64decode(contracifrada)
                    #iv = base64.b64decode(iv)
                    contradescifrada = descifrar(contracifrada, contram, iv)
                    c = {'credenciales': credenciales,'contradescifrada': contradescifrada}
                    return render(request,t,c)
                except:
                    errores =['Ocurrio un error comunicate con el administrador']
                    c = {'errores': errores}
                    return render(request,t,c)
            else:
                usuariopw = models.usuarios.objects.get(usuario=usuariocookie)
                pk = usuariopw.id
                credenciales = models.credenciales.objects.all().filter(usuario_asociado=pk).filter(nombre_cuenta=nombreCuenta).filter(usuario_cuenta=usuarioCuenta)
                #print(credencial.nombre_cuenta)
                errores = ['Contraseña invalida']
                c = {'okay': True,'contracifrada': True,'erroresf2': errores,'credenciales': credenciales}
                return render(request,t,c)
        elif request.POST.get("form_type") == 'formTres':
            try:
                usuariopw = models.usuarios.objects.get(usuario=usuariocookie)
                pk = usuariopw.id
                credenciales = models.credenciales.objects.all().filter(usuario_asociado=pk).filter(nombre_cuenta=nombreCuenta).filter(usuario_cuenta=usuarioCuenta)
                #print(credencial.nombre_cuenta)
                c = {'contracifrada': True, 'credenciales': credenciales}
                return render(request,t,c)
            except:
                errores =['Ocurrio un error comunicate con el administrador']
                c = {'errores': errores}
                return render(request,t,c)
        return render(request,t)

#----------------------------------------------------------------
@login_requerido
def compartir(request):
    if request.method == 'GET':
        t = 'compartir.html'
        return render(request,t)
    elif request.method == 'POST':
        t = 'registrar.html'
        return render(request,t)
