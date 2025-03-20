from django.db import models

class Usuario(models.Model):
    usuario_id = models.AutoField(primary_key=True)
    nombre_usuario = models.CharField(max_length=255, unique=True)
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

    def __str__(self):
        return self.nombre_usuario
