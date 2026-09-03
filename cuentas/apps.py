from django.apps import AppConfig


class CuentasConfig(AppConfig):
    name = 'cuentas'

    def ready(self):
        # Conecta el signal que crea el Perfil al crear un User.
        import cuentas.models  # noqa: F401