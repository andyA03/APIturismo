from django.contrib import admin

from django.contrib import admin
from .models import *

admin.site.register(Usuario)
admin.site.register(Destino)
admin.site.register(Itinerario)
admin.site.register(ItinerarioDestino)
admin.site.register(Post)
admin.site.register(Respuesta)