from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.index, name='index'),
    path('turno/<int:pk>/pdf/', views.cierre_turno_pdf, name='cierre_turno_pdf'),
    path('ventas/excel/', views.ventas_excel, name='ventas_excel'),
    path('inventario/excel/', views.inventario_excel, name='inventario_excel'),
]