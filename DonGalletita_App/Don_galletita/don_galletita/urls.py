"""
URL configuration for don_galletita project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cuentas/', include('django.contrib.auth.urls')),
    path('cuentas/registro/', views.registro, name="registro"),
    path('registro/', views.registro, name='registro'),
    path('', include('usuarios_app.urls')),
    path('insumos/', include('insumos_app.urls'), name='lista_insumo'),
    path('proveedores/', include('proveedores_app.urls')),
    path('productos/', include('productos_app.urls')),
    path('produccion/', include('produccion_app.urls')),
    path('clientes/', include('cliente_app.urls')),
    path('compras/', include('compras_app.urls')),
    path('ventas/', include('ventas_app.urls')),
    path('recetas/', include('recetas_app.urls')),
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

handler404 = views.custom_404
handler500 = views.custom_500
