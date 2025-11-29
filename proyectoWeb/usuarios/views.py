from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Usuario, Refaccion
import json
import pandas as pd

# --------------------------------------------------------------------------
# VISTA: Lista de usuarios y creación de usuario
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
                'usuarioId': usuario.usuario_id
            }, status=200)

        return JsonResponse({'error': 'Credenciales incorrectas'}, status=401)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTA: Crear refacción
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def crear_refaccion(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        usuario_id = data.get('usuario_id')

        if not usuario_id:
            return JsonResponse({'error': 'usuario_id es requerido'}, status=400)

        nueva_refaccion = Refaccion.objects.create(
            descripcion=data.get('descripcion'),
            costo=data.get('costo'),
            area=data.get('area'),
            consumo=data.get('consumo'),
            frecuencia=data.get('frecuencia'),
            unidad=data.get('unidad'),
            cantidad=data.get('cantidad'),
            observacion=data.get('observacion'),
            numero_parte_proveedor=data['numero_parte_proveedor'],
            marca_proveedor=data.get('marca_proveedor'),
            equipos_a_usar=data.get('equipos_a_usar'),
            familia=data.get('familia'),
            reemplazable=data.get('reemplazable'),
            reduce_velocidad=data.get('reduce_velocidad'),
            existe_riesgo=data.get('existe_riesgo'),
            nacionalidad=data.get('nacionalidad'),
            pagina_web=data.get('pagina_web'),
            usuario_id=usuario_id
        )
        return JsonResponse({'mensaje': 'Refacción creada', 'id': nueva_refaccion.id}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTA: Mis Refacciones (Listar por Usuario)
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["GET"])
def mis_refacciones(request, usuario_id):
    try:
        refacciones = Refaccion.objects.filter(usuario_id=usuario_id).values()
        return JsonResponse(list(refacciones), safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTA: Descargar Excel (Personal)
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["GET"])
def descargar_excel(request, usuario_id):
    try:
        refacciones = Refaccion.objects.filter(usuario_id=usuario_id).values()

        if not refacciones:
            return JsonResponse({'error': 'No hay datos para exportar'}, status=404)

        df = pd.DataFrame(refacciones)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="mis_refacciones.xlsx"'
        df.to_excel(response, index=False)

        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTA UNIFICADA: Detalle de Refacción (GET y PUT)
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["GET", "PUT"])
def detalle_refaccion(request, refaccion_id):
    if request.method == 'GET':
        try:
            r = Refaccion.objects.filter(id=refaccion_id).values().first()
            if not r:
                return JsonResponse({'error': 'Refacción no encontrada'}, status=404)
            return JsonResponse(r, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    if request.method == 'PUT':
        try:
            data = json.loads(request.body.decode('utf-8'))
            rows_updated = Refaccion.objects.filter(id=refaccion_id).update(**data)
            
            if rows_updated == 0:
                return JsonResponse({'error': 'No se pudo actualizar o no existe el ID'}, status=404)

            return JsonResponse({'mensaje': 'Refacción actualizada correctamente'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# ==========================================================================
#  [cite_start]NUEVAS VISTAS PARA "TODOS LOS REGISTROS" (GLOBALES) [cite: 106, 113]
# ==========================================================================

@csrf_exempt
@require_http_methods(["GET"])
def todas_refacciones(request):
    try:
        # Trae TODOS los registros sin filtrar por usuario
        refacciones = Refaccion.objects.all().values()
        return JsonResponse(list(refacciones), safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def descargar_excel_global(request):
    try:
        refacciones = Refaccion.objects.all().values()

        if not refacciones:
            return JsonResponse({'error': 'No hay datos para exportar'}, status=404)

        df = pd.DataFrame(refacciones)

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="todas_refacciones.xlsx"'
        df.to_excel(response, index=False)

        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)