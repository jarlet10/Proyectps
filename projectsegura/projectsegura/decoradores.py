from django.shortcuts import redirect





def login_requerido(vista):
    def intena(request, *args, **kwargs):
        logueado = request.session.get('logueado', False)
        if not logueado:
            return redirect('/iniciar_sesion')
        return vista(request,*args, **kwargs) #continuar ejecucion normal
    return intena

