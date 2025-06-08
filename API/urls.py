from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import *


router = SimpleRouter()

router.register(r'destinos', DestinoViewSet, basename='destinos')
router.register(r'itinerarios', ItinerarioViewSet, basename='itinerarios')
router.register(r'itinerario-destinos', ItinerarioDestinoViewSet, basename='itinerarios-destinos')
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'respuestas', RespuestaViewSet, basename='respuestas')


urlpatterns = [
    path('API/', include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),  
    path("login/", LoginView.as_view(), name="login"),  
    path("manage/", UserManagementView.as_view(), name="manage"), 
    path('auth/register/', RegisterView.as_view(), name='register'),  
    path('auth/login/', LoginView.as_view(), name='login'),
    path('user/', UserManagementView.as_view(), name='user-management')            
]