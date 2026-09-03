"""
Arranca el sistema con waitress (servidor WSGI apto para uso diario en
Windows, a diferencia de `manage.py runserver` que es solo para desarrollo).

Uso en la PC servidor:
    python serve_waitress.py

Desde la otra PC, en el navegador:
    http://<IP_DE_LA_PC_SERVIDOR>:8000
"""
import os

from waitress import serve

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django  # noqa: E402

django.setup()

from config.wsgi import application  # noqa: E402

if __name__ == '__main__':
    HOST = '0.0.0.0'  # escucha en todas las interfaces de red, no solo localhost
    PORT = 8000

    print(f'Sirviendo Librería Ventura en http://{HOST}:{PORT}')
    print('Desde la otra PC entra a la IP de esta máquina, ej: http://192.168.1.50:8000')

    serve(application, host=HOST, port=PORT)
