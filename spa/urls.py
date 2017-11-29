"""rodgal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from inv import (views, ventas, compras, pagos, caja, productos, servicios, paquetes, sesiones, ordenes, clientes,
                 panelclientes, panelcolaborador, proveedores, cajeros, consultas, estadisticas)

from spa.settings import STATIC_URL, STATIC_ROOT, MEDIA_URL, MEDIA_ROOT

urlpatterns = [

    # Admin
    url(r'^admin/', include(admin.site.urls)),

    # Home
    url(r'^$', views.index, name='index'),

    # Login
    url(r'^login$', views.login_user, name='login_user'),

    # Logout
    url(r'^logout$', views.logout_user, name='logout_user'),

    # Change passw
    url(r'^pass$', views.passwd, name='change_password'),

    # Get Data API
    url(r'^get_data$', views.get_data, name='get_data'),

    # Subir Video
    url(r'^subir_video$', views.subir_video, name='subir_video'),

    # VENTAS
    url(r'^ventas$', ventas.view, name='ventas'),

    # COMPRAS
    url(r'^compras$', compras.view, name='compras'),

    # PAGOS
    url(r'^pagos$', pagos.view, name='pagos'),

    # SESION DE CAJA
    url(r'^caja', caja.view, name='caja'),

    # GESTION DE PRODUCTOS
    url(r'^productos$', productos.view, name='productos'),

    # SERVICIOS
    url(r'^servicios$', servicios.view, name='servicios'),

    # PAQUETES
    url(r'^paquetes$', paquetes.view, name='paquetes'),

    # SESIONES
    url(r'^sesiones$', sesiones.view, name='sesiones'),

    # ORDENES DE SERVICIOS
    url(r'^ordenes$', ordenes.view, name='ordenes'),

    # CLIENTES
    url(r'^clientes$', clientes.view, name='clientes'),

    # PANEL CLIENTES
    url(r'^panelclientes$', panelclientes.view, name='panelclientes'),

    # PANEL COLABORADORES
    url(r'^panelcolaborador$', panelcolaborador.view, name='panelcolaborador'),

    # PROVEEDORES
    url(r'^proveedores$', proveedores.view, name='proveedores'),

    # CAJEROS
    url(r'^cajeros$', cajeros.view, name='cajeros'),

    # CONSULTAS
    url(r'^consultas$', consultas.view, name='consultas'),

    # ESTADISTICAS Y GRAFICOS
    url(r'^estadisticas$', estadisticas.view, name='estadisticas'),

]

# Static
urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)

# Media
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)