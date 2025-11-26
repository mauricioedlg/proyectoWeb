

from django.contrib import admin
from django.urls import path
from usuarios import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usuarios/', views.lista_usuarios),
    path('api/login/', views.login_usuario),
    path('api/refacciones/', views.crear_refaccion),
    path('api/mis_refacciones/<int:usuario_id>/', views.mis_refacciones),
]