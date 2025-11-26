from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Usuario, Refaccion
import json

@csrf_exempt
@require_http_methods(["GET", "POST"])
def lista_usuarios(request):
    if request.method == 'GET':
        usuarios = Usuario.objects.all().values()
        return JsonResponse(list(usuarios), safe=False)

    # POST: crear usuario
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
        else:
            return JsonResponse({'error': 'Credenciales incorrectas'}, status=401)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

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

@csrf_exempt
@require_http_methods(["GET"])
def mis_refacciones(request, usuario_id):
    try:
        refacciones = Refaccion.objects.filter(usuario_id=usuario_id).values()
        return JsonResponse(list(refacciones), safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)