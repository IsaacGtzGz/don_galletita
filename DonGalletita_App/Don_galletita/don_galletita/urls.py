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
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('usuarios/', include('usuarios_app.urls')),
    path('login/', include('django.contrib.auth.urls'), name="login"),
    path('cuentas/', include('django.contrib.auth.urls')),
    path('cuentas/registro/', views.registro, name="registro"),
    path('proveedores/', include('proveedores_app.urls')),
    path('clientes/', include('clientes.urls')),
    path('insumos/', include('insumos_app.urls'), name='lista_insumo'),
]
