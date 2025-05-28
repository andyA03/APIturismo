from rest_framework import serializers
from .models import Usuario, Destino, Itinerario, ItinerarioDestino, Post, Respuesta
from django.contrib.auth.hashers import make_password

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'usuario_id', 
            'nombre', 
            'apellido', 
            'email', 
            'contrasena',
            'fecha_nacimiento',
            'pais_origen',
            'fecha_registro',
            'ultimo_acceso',
            'foto_perfil'
        ]
        extra_kwargs = {
            'contrasena': {'write_only': True},
            'fecha_registro': {'read_only': True}
        }

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado")
        return value

    def create(self, validated_data):
        validated_data['contrasena'] = make_password(validated_data['contrasena'])
        return super().create(validated_data)

class DestinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destino
        fields = [
            'destino_id',
            'nombre',
            'provincia',
            'descripcion',
            'destacado',
            'imagen_principal',
            'galeria_imagenes',
            'categoria',
            'calificacion'
        ]

class ItinerarioSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Itinerario
        fields = [
            'itinerario_id',
            'usuario',
            'titulo',
            'fecha_creacion',
            'compartido'
        ]
        read_only_fields = ['fecha_creacion']

class ItinerarioDestinoSerializer(serializers.ModelSerializer):
    destino = DestinoSerializer(read_only=True)
    destino_id = serializers.PrimaryKeyRelatedField(
        queryset=Destino.objects.all(),
        source='destino',
        write_only=True
    )
    
    class Meta:
        model = ItinerarioDestino
        fields = [
            'id',
            'itinerario',
            'destino',
            'destino_id',
            'orden'
        ]
        extra_kwargs = {
            'itinerario': {'read_only': True}
        }

class PostSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)
    destino = DestinoSerializer(read_only=True)
    destino_id = serializers.PrimaryKeyRelatedField(
        queryset=Destino.objects.all(),
        source='destino',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Post
        fields = [
            'post_id',
            'usuario',
            'destino',
            'destino_id',
            'contenido',
            'fecha_publicacion',
            'likes'
        ]
        read_only_fields = ['fecha_publicacion', 'likes']

class RespuestaSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Respuesta
        fields = [
            'id_respuesta',
            'usuario',
            'post',
            'contenido',
            'fecha_creacion'
        ]
        read_only_fields = ['fecha_creacion']

# Serializadores para relaciones anidadas
class ItinerarioConDestinosSerializer(ItinerarioSerializer):
    destinos = serializers.SerializerMethodField()
    
    class Meta(ItinerarioSerializer.Meta):
        fields = ItinerarioSerializer.Meta.fields + ['destinos']
    
    def get_destinos(self, obj):
        destinos = ItinerarioDestino.objects.filter(itinerario=obj).order_by('orden')
        return ItinerarioDestinoSerializer(destinos, many=True).data

class PostConRespuestasSerializer(PostSerializer):
    respuestas = serializers.SerializerMethodField()
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['respuestas']
    
    def get_respuestas(self, obj):
        respuestas = Respuesta.objects.filter(post=obj)
        return RespuestaSerializer(respuestas, many=True).data