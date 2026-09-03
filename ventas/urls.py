from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('nueva/', views.nueva_venta, name='nueva'),
    path('<int:pk>/', views.detalle_venta, name='detalle'),
    path('<int:pk>/anular/', views.anular_venta, name='anular'),
]