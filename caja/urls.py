from django.urls import path
from . import views

app_name = 'caja'

urlpatterns = [
    path('turno/', views.turno_actual, name='turno_actual'),
    path('turno/abrir/', views.abrir_turno, name='abrir_turno'),
    path('turno/cerrar/', views.cerrar_turno, name='cerrar_turno'),
    path('turno/<int:pk>/cerrar/', views.cerrar_turno, name='cerrar_turno_admin'),
    path('turno/<int:pk>/resumen/', views.resumen_cierre, name='resumen_cierre'),
    path('turnos/', views.lista_turnos, name='lista_turnos'),
]