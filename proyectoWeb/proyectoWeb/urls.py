from django.contrib import admin
from django.urls import path
from usuarios import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/usuarios/', views.lista_usuarios),
    path('api/login/', views.login_usuario),
    path('api/refacciones/', views.crear_refaccion),
    path('api/mis_refacciones/<int:usuario_id>/', views.mis_refacciones),
    path('api/descargar_excel/<int:usuario_id>/', views.descargar_excel),
    path('api/refaccion/<int:refaccion_id>/', views.detalle_refaccion),

    path('api/todas_refacciones/', views.todas_refacciones),
    path('api/descargar_excel_global/', views.descargar_excel_global),

    # RUTAS GERENTE MANTENIMIENTO
    path('api/pendientes_aprobacion/', views.pendientes_aprobacion),
    path('api/gestionar_aprobacion/<int:refaccion_id>/', views.gestionar_aprobacion),

    # NUEVAS RUTAS GERENTE PLANTA
    path('api/pendientes_aprobacion_planta/', views.pendientes_aprobacion_planta),
    path('api/gestionar_aprobacion_planta/<int:refaccion_id>/', views.gestionar_aprobacion_planta),

    # RUTAS NOTIFICACIONES
    path('api/notificaciones/<int:usuario_id>/', views.obtener_notificaciones),
    path('api/notificaciones/leer/<int:notificacion_id>/', views.leer_notificacion),
]