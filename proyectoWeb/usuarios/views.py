from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Usuario, Refaccion
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
                'usuarioId': usuario.usuario_id
            }, status=200)
        return JsonResponse({'error': 'Credenciales incorrectas'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTA: Crear Refacción (POST)
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
            usuario_id=usuario_id
        )
        return JsonResponse({'mensaje': 'Refacción creada', 'id': nueva_refaccion.id}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTA: Mis Refacciones (Listar) -> CORREGIDO: Excluye PDF
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["GET"])
def mis_refacciones(request, usuario_id):
    try:
        # Obtenemos todos los valores
        refacciones = list(Refaccion.objects.filter(usuario_id=usuario_id).values())
        
        # Eliminamos el campo binario de cada registro para que JSON no falle
        for ref in refacciones:
            if 'archivo_pdf' in ref:
                del ref['archivo_pdf']

        return JsonResponse(refacciones, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTA: Todas las Refacciones (Globales) -> CORREGIDO: Excluye PDF
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["GET"])
def todas_refacciones(request):
    try:
        refacciones = list(Refaccion.objects.all().values())
        
        # Eliminamos el campo binario
        for ref in refacciones:
            if 'archivo_pdf' in ref:
                del ref['archivo_pdf']

        return JsonResponse(refacciones, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# --------------------------------------------------------------------------
# VISTA: Descargar Excel Personal -> CORREGIDO: Excluye PDF
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["GET"])
def descargar_excel(request, usuario_id):
    try:
        refacciones = list(Refaccion.objects.filter(usuario_id=usuario_id).values())

        if not refacciones:
            return JsonResponse({'error': 'No hay datos para exportar'}, status=404)

        # Limpiamos binarios antes de crear el Excel
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

# --------------------------------------------------------------------------
# VISTA: Descargar Excel Global -> CORREGIDO: Excluye PDF
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["GET"])
def descargar_excel_global(request):
    try:
        refacciones = list(Refaccion.objects.all().values())

        if not refacciones:
            return JsonResponse({'error': 'No hay datos para exportar'}, status=404)

        # Limpiamos binarios
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

# --------------------------------------------------------------------------
# VISTA UNIFICADA: Detalle de Refacción (GET y POST)
# --------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["GET", "POST"])
def detalle_refaccion(request, refaccion_id):
    
    # 1. Obtener datos (GET) -> Ya incluía limpieza, la mantenemos
    if request.method == 'GET':
        try:
            r = Refaccion.objects.filter(id=refaccion_id).values().first()
            if not r:
                return JsonResponse({'error': 'Refacción no encontrada'}, status=404)
            
            if 'archivo_pdf' in r:
                del r['archivo_pdf'] 
                
            return JsonResponse(r, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    # 2. Editar datos (POST)
    if request.method == 'POST':
        try:
            refaccion = Refaccion.objects.filter(id=refaccion_id).first()
            if not refaccion:
                return JsonResponse({'error': 'Refacción no encontrada'}, status=404)

            data = request.POST
            archivo = request.FILES.get('archivo_pdf')

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