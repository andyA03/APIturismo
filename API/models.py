from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin, models.Model):
    usuario_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.CharField(max_length=255, unique=True)
    contrasena = models.CharField(max_length=255,)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    pais_origen = models.CharField(max_length=100, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    foto_perfil = models.CharField(max_length=255, null=True, blank=True)


    USERNAME_FIELD = "email"
    objects = CustomUserManager()

    def str(self):
        return self.email


class Destino(models.Model):
    destino_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    provincia = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField()
    destacado = models.BooleanField(default=False)
    imagen_principal = models.CharField(max_length=255, null=True, blank=True)
    galeria_imagenes = models.TextField(null=True, blank=True)
    categoria = models.CharField(max_length=50, null=True, blank=True)
    calificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class Itinerario(models.Model):
    itinerario_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    compartido = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo

class ItinerarioDestino(models.Model):
    itinerario = models.ForeignKey(Itinerario, on_delete=models.CASCADE)
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE)
    orden = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = (('itinerario', 'destino'),)

    def __str__(self):
        return f"{self.itinerario.titulo} - {self.destino.nombre}"

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    destino = models.ForeignKey(Destino, on_delete=models.SET_NULL, null=True, blank=True)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return f"Post #{self.post_id}"

class Respuesta(models.Model):
    id_respuesta = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Respuesta #{self.id_respuesta}"