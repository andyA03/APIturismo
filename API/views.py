from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from .models import Usuario, Destino, Itinerario, ItinerarioDestino, Post, Respuesta
from .serializers import (
    UsuarioSerializer,
    DestinoSerializer,
    ItinerarioSerializer,
    ItinerarioDestinoSerializer,
    ItinerarioConDestinosSerializer,
    PostSerializer,
    PostConRespuestasSerializer,
    RespuestaSerializer
)

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar usuarios con validaciones de contraseña y email único.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        """Hashea la contraseña al crear usuario"""
        request.data['contrasena'] = make_password(request.data['contrasena'])
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Hashea la contraseña al actualizar usuario"""
        if 'contrasena' in request.data:
            request.data['contrasena'] = make_password(request.data['contrasena'])
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['GET'])
    def me(self, request):
        """Endpoint para obtener datos del usuario logueado"""
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response(
            {"error": "No estás autenticado"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

class DestinoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para destinos con permisos básicos.
    """
    queryset = Destino.objects.all()
    serializer_class = DestinoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['provincia', 'categoria', 'destacado']

    @action(detail=True, methods=['GET'])
    def itinerarios(self, request, pk=None):
        """Obtiene todos los itinerarios que incluyen este destino"""
        destino = self.get_object()
        itinerarios = ItinerarioDestino.objects.filter(destino=destino)
        serializer = ItinerarioDestinoSerializer(itinerarios, many=True)
        return Response(serializer.data)

class ItinerarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para itinerarios con validación de propiedad.
    """
    serializer_class = ItinerarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Solo muestra itinerarios del usuario actual"""
        return Itinerario.objects.filter(usuario=self.request.user)

    def get_serializer_class(self):
        """Usa serializer con destinos anidados para detalles"""
        if self.action in ['retrieve', 'list']:
            return ItinerarioConDestinosSerializer
        return ItinerarioSerializer

    def perform_create(self, serializer):
        """Asigna automáticamente el usuario al crear"""
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=['POST'])
    def add_destino(self, request, pk=None):
        """Añade un destino al itinerario con validación"""
        itinerario = self.get_object()
        destino = get_object_or_404(Destino, destino_id=request.data.get('destino_id'))
        
        if ItinerarioDestino.objects.filter(itinerario=itinerario, destino=destino).exists():
            return Response(
                {"error": "Este destino ya está en el itinerario"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        itinerario_destino = ItinerarioDestino.objects.create(
            itinerario=itinerario,
            destino=destino,
            orden=request.data.get('orden', 0)
        )
        serializer = ItinerarioDestinoSerializer(itinerario_destino)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ItinerarioDestinoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para relación Itinerario-Destino con validaciones.
    """
    serializer_class = ItinerarioDestinoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Solo muestra relaciones de itinerarios del usuario"""
        return ItinerarioDestino.objects.filter(itinerario__usuario=self.request.user)

    def perform_destroy(self, instance):
        """Valida propiedad antes de eliminar"""
        if instance.itinerario.usuario == self.request.user:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "No tienes permiso para esta acción"},
            status=status.HTTP_403_FORBIDDEN
        )

class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet para posts con sistema de likes.
    """
    queryset = Post.objects.all().order_by('-fecha_publicacion')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Usa serializer con respuestas para detalles"""
        if self.action == 'retrieve':
            return PostConRespuestasSerializer
        return PostSerializer

    def perform_create(self, serializer):
        """Asigna usuario automáticamente"""
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=['POST'])
    def toggle_like(self, request, pk=None):
        """Alterna like del usuario en el post"""
        post = self.get_object()
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return Response({"likes": post.likes.count()})

class RespuestaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para respuestas a posts.
    """
    serializer_class = RespuestaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filtra respuestas por post"""
        return Respuesta.objects.filter(post_id=self.kwargs['post_pk'])

    def perform_create(self, serializer):
        """Asigna usuario y post automáticamente"""
        post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        serializer.save(usuario=self.request.user, post=post)