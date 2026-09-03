# Librería Ventura — Setup

Sistema de punto de venta para librería, pensado para correr en una PC
"servidor" dentro de una red local de 2 computadoras.

## 1. Instalación (en la PC servidor)

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

## 2. Primera vez

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## 3. Arrancar el sistema

Para uso diario, **no uses** `python manage.py runserver` (es solo para
desarrollo). Usa:

```bash
python serve_waitress.py
```

Esto deja el sistema escuchando en el puerto 8000 de todas las interfaces
de red de esa PC.

## 4. Configurar la PC servidor (una sola vez)

### 4.1 IP fija o reservada
La PC servidor necesita que su IP en la red local no cambie, porque la otra
PC se va a conectar a esa dirección. Dos formas de lograrlo:
- **Recomendado:** entra al router y reserva una IP fija para la MAC de esa
  PC (DHCP reservation). Así sigues usando DHCP pero la IP nunca cambia.
- **Alternativa:** configura una IP estática manualmente en Windows
  (Panel de Control > Centro de redes > Cambiar configuración del adaptador).

### 4.2 Abrir el puerto en el Firewall de Windows
Sin esto, la otra PC no va a poder conectarse aunque el servidor esté
corriendo. Desde una terminal con permisos de administrador en la PC
servidor:

```bash
netsh advfirewall firewall add rule name="Libreria Ventura" dir=in action=allow protocol=TCP localport=8000
```

### 4.3 Confirmar la IP de la PC servidor

```bash
ipconfig
```

Busca la "Dirección IPv4" (algo como `192.168.1.50`).

## 5. Desde la segunda PC

Solo necesita un navegador. Entra a:

```
http://192.168.1.50:8000
```

(sustituye por la IP real de la PC servidor del paso 4.3)

## Estructura del proyecto

```
libreria_ventura/
├── manage.py
├── serve_waitress.py        # arranque para uso diario (LAN)
├── requirements.txt
├── config/                  # settings, urls raíz
├── productos/                # catálogo: nombre, precio, stock, categoría
├── ventas/                   # Venta y DetalleVenta, descuenta stock
├── caja/                     # Caja, Turno, MovimientoCaja, lógica de cierre
├── reportes/                 # vistas que generan Excel/PDF (sin modelos propios)
├── templates/                # templates compartidos + una carpeta por app
└── static/                   # CSS/JS/imágenes propias del proyecto
```

## Próximos pasos

- Modelos de datos (`Caja`, `Turno`, `MovimientoCaja`, `Producto`, `Venta`,
  `DetalleVenta`).
- Login y roles (`Perfil` con admin/cajero + decorador de permisos).
- Flujo de venta y descuento de stock.
- Reportes en Excel (openpyxl) y PDF (reportlab).
