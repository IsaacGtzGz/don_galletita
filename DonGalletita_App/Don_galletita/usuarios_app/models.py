from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, contrasenia=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(contrasenia)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, contrasenia=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(username, email, contrasenia, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    usuario_id = models.AutoField(primary_key=True)
    nombre_usuario = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    contrasenia = models.CharField(max_length=255)
    rol = models.CharField(
        max_length=10,
        choices=[
            ('admin', 'Admin'),
            ('empleado', 'Empleado'),
            ('cliente', 'Cliente')
        ],
        default='cliente'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estatus_user = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.nombre_usuario
