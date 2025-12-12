from django.apps import AppConfig


class RentalConfig(AppConfig):
    name = 'rental'
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Rental Mobil'
    
    def ready(self):
        # Import signals saat aplikasi ready
        import rental.signals  # noqa
