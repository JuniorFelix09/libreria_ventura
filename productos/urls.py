from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.lista_productos, name='lista'),
    path('crear/', views.crear_producto, name='crear'),
    path('<int:pk>/editar/', views.editar_producto, name='editar'),
    path('<int:pk>/toggle/', views.toggle_activo, name='toggle_activo'),
    path('categoria/crear/', views.crear_categoria, name='crear_categoria'),
]