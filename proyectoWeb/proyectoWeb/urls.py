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

    # --- NUEVAS RUTAS PARA GERENTE ---
    path('api/pendientes_aprobacion/', views.pendientes_aprobacion),
    path('api/gestionar_aprobacion/<int:refaccion_id>/', views.gestionar_aprobacion),
]