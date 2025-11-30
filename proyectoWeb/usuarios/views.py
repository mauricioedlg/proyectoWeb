from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Usuario, Refaccion, Notificacion
import json
import pandas as pd

# --------------------------------------------------------------------------
# VISTA: Lista de usuarios
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["GET", "POST"])
def lista_usuarios(request):
    if request.method == 'GET':
        usuarios = Usuario.objects.all().values()
        return JsonResponse(list(usuarios), safe=False)
    try:
        data = json.loads(request.body.decode('utf-8'))
        nuevo_usuario = Usuario.objects.create(
            username=data['username'],
            correo=data['correo'],
            contrasena=data['contrasena'],
            nombre=data['nombre'],
            apellidos=data['apellidos'],
            rol=data['rol'],
            descripcion_rol=data.get('descripcion_rol', ''),
            numero_de_sitio=data['numero_de_sitio']
        )
        return JsonResponse({'mensaje': 'Usuario creado correctamente', 'id': nuevo_usuario.usuario_id}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTA: Login
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def login_usuario(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        contrasena = data.get('contrasena')
        usuario = Usuario.objects.filter(username=username, contrasena=contrasena).first()
        if usuario:
            return JsonResponse({
                'mensaje': 'Login exitoso',
                'nombre': usuario.nombre,
                'usuarioId': usuario.usuario_id,
                'rol': usuario.rol,
                'descripcion_rol': usuario.descripcion_rol
            }, status=200)
        return JsonResponse({'error': 'Credenciales incorrectas'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTA: Crear Refacción
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def crear_refaccion(request):
    try:
        data = request.POST
        usuario_id = data.get('usuario_id')
        archivo = request.FILES.get('archivo_pdf')

        if not usuario_id:
            return JsonResponse({'error': 'usuario_id es requerido'}, status=400)

        contenido_pdf = None
        if data.get('familia') == 'Quimicos' and archivo:
            contenido_pdf = archivo.read()

        nueva_refaccion = Refaccion.objects.create(
            descripcion=data.get('descripcion'),
            costo=data.get('costo') if data.get('costo') else None,
            area=data.get('area'),
            consumo=data.get('consumo'),
            frecuencia=data.get('frecuencia'),
            unidad=data.get('unidad'),
            cantidad=data.get('cantidad') if data.get('cantidad') else None,
            observacion=data.get('observacion'),
            numero_parte_proveedor=data.get('numero_parte_proveedor'),
            marca_proveedor=data.get('marca_proveedor'),
            equipos_a_usar=data.get('equipos_a_usar'),
            familia=data.get('familia'),
            reemplazable=data.get('reemplazable'),
            reduce_velocidad=data.get('reduce_velocidad'),
            existe_riesgo=data.get('existe_riesgo'),
            nacionalidad=data.get('nacionalidad'),
            pagina_web=data.get('pagina_web'),
            archivo_pdf=contenido_pdf,
            usuario_id=usuario_id,
            aprobacion_mtto='PENDIENTE',
            aprobacion_planta='PENDIENTE'
        )

        # NOTIFICAR GERENTE MANTENIMIENTO
        gerentes = Usuario.objects.filter(descripcion_rol='Gerente Mantenimiento')
        
        solicitante = Usuario.objects.filter(usuario_id=usuario_id).first()
        nombre_solicitante = f"{solicitante.nombre} {solicitante.apellidos}" if solicitante else "Un usuario"

        for gerente in gerentes:
            Notificacion.objects.create(
                usuario=gerente,
                mensaje=f"Nuevo registro de: {nombre_solicitante}. Ref: {nueva_refaccion.descripcion}",
                url_destino="aprobaciones_pendientes.html"
            )

        return JsonResponse({'mensaje': 'Refacción creada', 'id': nueva_refaccion.id}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTAS: Consultas (Mis Refacciones / Todas)
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["GET"])
def mis_refacciones(request, usuario_id):
    try:
        refacciones = list(Refaccion.objects.filter(usuario_id=usuario_id).values())
        for ref in refacciones:
            if 'archivo_pdf' in ref:
                del ref['archivo_pdf']
        return JsonResponse(refacciones, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def todas_refacciones(request):
    try:
        refacciones = list(Refaccion.objects.all().values())
        for ref in refacciones:
            if 'archivo_pdf' in ref:
                del ref['archivo_pdf']
        return JsonResponse(refacciones, safe=False, status=200)
    except Exception as e:
         return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def descargar_excel(request, usuario_id):
    try:
        refacciones = list(Refaccion.objects.filter(usuario_id=usuario_id).values())
        if not refacciones:
            return JsonResponse({'error': 'No hay datos para exportar'}, status=404)
        for ref in refacciones:
            if 'archivo_pdf' in ref:
                del ref['archivo_pdf']
        df = pd.DataFrame(refacciones)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="mis_refacciones.xlsx"'
        df.to_excel(response, index=False)
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def descargar_excel_global(request):
    try:
        refacciones = list(Refaccion.objects.all().values())
        if not refacciones:
            return JsonResponse({'error': 'No hay datos para exportar'}, status=404)
        for ref in refacciones:
            if 'archivo_pdf' in ref:
                del ref['archivo_pdf']
        df = pd.DataFrame(refacciones)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="todas_refacciones.xlsx"'
        df.to_excel(response, index=False)
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def detalle_refaccion(request, refaccion_id):
    if request.method == 'GET':
        try:
            data = Refaccion.objects.filter(id=refaccion_id).values().first()
            if not data:
                return JsonResponse({'error': 'Refacción no encontrada'}, status=404)
            if 'archivo_pdf' in data:
                del data['archivo_pdf'] 
            try:
                usuario = Usuario.objects.get(usuario_id=data['usuario_id'])
                data['nombre_solicitante'] = f"{usuario.nombre} {usuario.apellidos}"
            except Usuario.DoesNotExist:
                data['nombre_solicitante'] = "Usuario Desconocido"
            return JsonResponse(data, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    if request.method == 'POST':
        try:
            refaccion = Refaccion.objects.filter(id=refaccion_id).first()
            if not refaccion:
                return JsonResponse({'error': 'Refacción no encontrada'}, status=404)
            data = request.POST
            archivo = request.FILES.get('archivo_pdf')

            # Actualización campos
            refaccion.descripcion = data.get('descripcion', refaccion.descripcion)
            refaccion.costo = data.get('costo', refaccion.costo)
            refaccion.area = data.get('area', refaccion.area)
            refaccion.consumo = data.get('consumo', refaccion.consumo)
            refaccion.frecuencia = data.get('frecuencia', refaccion.frecuencia)
            refaccion.unidad = data.get('unidad', refaccion.unidad)
            refaccion.cantidad = data.get('cantidad', refaccion.cantidad)
            refaccion.observacion = data.get('observacion', refaccion.observacion)
            refaccion.numero_parte_proveedor = data.get('numero_parte_proveedor', refaccion.numero_parte_proveedor)
            refaccion.marca_proveedor = data.get('marca_proveedor', refaccion.marca_proveedor)
            refaccion.equipos_a_usar = data.get('equipos_a_usar', refaccion.equipos_a_usar)
            refaccion.familia = data.get('familia', refaccion.familia)
            refaccion.reemplazable = data.get('reemplazable', refaccion.reemplazable)
            refaccion.reduce_velocidad = data.get('reduce_velocidad', refaccion.reduce_velocidad)
            refaccion.existe_riesgo = data.get('existe_riesgo', refaccion.existe_riesgo)
            refaccion.nacionalidad = data.get('nacionalidad', refaccion.nacionalidad)
            refaccion.pagina_web = data.get('pagina_web', refaccion.pagina_web)

            if data.get('familia') == 'Quimicos' and archivo:
                refaccion.archivo_pdf = archivo.read()
            elif data.get('familia') != 'Quimicos':
                refaccion.archivo_pdf = None

            refaccion.save()
            return JsonResponse({'mensaje': 'Refacción actualizada correctamente'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTAS: Aprobación MANTENIMIENTO
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["GET"])
def pendientes_aprobacion(request):
    try:
        # Solo lo que no ha revisado Mtto
        refs_qs = Refaccion.objects.filter(aprobacion_mtto='PENDIENTE').select_related('usuario')
        lista_final = []
        for r in refs_qs:
            lista_final.append({
                'id': r.id,
                'descripcion': r.descripcion,
                'usuario_id': r.usuario_id,
                'nombre_solicitante': f"{r.usuario.nombre} {r.usuario.apellidos}",
                'aprobacion_mtto': r.aprobacion_mtto
            })
        return JsonResponse(lista_final, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def gestionar_aprobacion(request, refaccion_id):
    try:
        data = json.loads(request.body.decode('utf-8'))
        accion = data.get('accion') 

        refaccion = Refaccion.objects.filter(id=refaccion_id).first()
        if not refaccion:
            return JsonResponse({'error': 'Refacción no encontrada'}, status=404)

        refaccion.aprobacion_mtto = accion
        refaccion.save()

        # LOGICA NOTIFICACION DE MANTENIMIENTO
        if accion == 'SI':
             # Si aprueba Mtto -> Notificar a Gerente Planta
             gerentes_planta = Usuario.objects.filter(descripcion_rol='Gerente Planta')
             for gp in gerentes_planta:
                 Notificacion.objects.create(
                     usuario=gp,
                     mensaje=f"Mtto Aprobado. Pendiente revisión Planta: {refaccion.descripcion}",
                     url_destino="aprobaciones_pendientes.html"
                 )
        else:
             # Si rechaza Mtto -> Notificar directo al Usuario
             Notificacion.objects.create(
                usuario=refaccion.usuario,
                mensaje=f"Tu refacción '{refaccion.descripcion}' fue RECHAZADA por Mantenimiento.",
                url_destino="mis_altas.html"
             )

        return JsonResponse({'mensaje': f'Mantenimiento: Refacción {accion}'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTAS: Aprobación PLANTA (NUEVO)
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["GET"])
def pendientes_aprobacion_planta(request):
    try:
        # Solo lo que YA aprobó Mtto pero NO ha revisado Planta
        refs_qs = Refaccion.objects.filter(aprobacion_mtto='SI', aprobacion_planta='PENDIENTE').select_related('usuario')
        lista_final = []
        for r in refs_qs:
            lista_final.append({
                'id': r.id,
                'descripcion': r.descripcion,
                'usuario_id': r.usuario_id,
                'nombre_solicitante': f"{r.usuario.nombre} {r.usuario.apellidos}",
                'aprobacion_mtto': r.aprobacion_mtto,
                'aprobacion_planta': r.aprobacion_planta
            })
        return JsonResponse(lista_final, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def gestionar_aprobacion_planta(request, refaccion_id):
    try:
        data = json.loads(request.body.decode('utf-8'))
        accion = data.get('accion') 

        refaccion = Refaccion.objects.filter(id=refaccion_id).first()
        if not refaccion:
            return JsonResponse({'error': 'Refacción no encontrada'}, status=404)

        refaccion.aprobacion_planta = accion
        refaccion.save()

        # LOGICA NOTIFICACION DE PLANTA -> SIEMPRE NOTIFICA AL USUARIO FINAL
        estado_texto = "APROBADO" if accion == "SI" else "RECHAZADO"
        Notificacion.objects.create(
            usuario=refaccion.usuario,
            mensaje=f"Tu refacción '{refaccion.descripcion}' fue revisada por Planta. Estatus: {estado_texto}",
            url_destino="mis_altas.html"
        )

        return JsonResponse({'mensaje': f'Planta: Refacción {accion}'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTAS: Notificaciones
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["GET"])
def obtener_notificaciones(request, usuario_id):
    try:
        notifs = list(Notificacion.objects.filter(usuario_id=usuario_id)
                      .order_by('leido', '-fecha').values())
        return JsonResponse(notifs, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def leer_notificacion(request, notificacion_id):
    try:
        n = Notificacion.objects.get(id=notificacion_id)
        n.leido = True
        n.save()
        return JsonResponse({'mensaje': 'Leido'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)