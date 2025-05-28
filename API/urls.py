from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    UsuarioViewSet,
    DestinoViewSet,
    ItinerarioViewSet,
    ItinerarioDestinoViewSet,
    PostViewSet,
    RespuestaViewSet
)

router = SimpleRouter()

# Registro básico de todos los viewsets
router.register(r'usuarios', UsuarioViewSet, 'usuarios')
router.register(r'destinos', DestinoViewSet, 'destinos')
router.register(r'itinerarios', ItinerarioViewSet, 'itinerarios')
router.register(r'itinerario-destinos', ItinerarioDestinoViewSet, 'itinerarios-destinos')
router.register(r'posts', PostViewSet, 'posts')
router.register(r'respuestas', RespuestaViewSet, 'respuestas')

urlpatterns = [
    path('API/', include(router.urls)),
]