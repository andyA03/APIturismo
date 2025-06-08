from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated , AllowAny
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import * 

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuario registrado correctamente."}, status=201)
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = User.objects.filter(email__iexact=email).first()
        if not user or not check_password(password, user.password):
            return Response({"error": "Correo o contraseña incorrectos"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({"refresh": str(refresh), "access": str(refresh.access_token)}, status=status.HTTP_200_OK)

class UserManagementView(APIView):
    permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "Usuario eliminado correctamente."}, status=status.HTTP_200_OK)

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
        return Respuesta.objects.all()

    def perform_create(self, serializer):
        """Asigna usuario y post automáticamente"""
        post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        serializer.save(usuario=self.request.user, post=post)