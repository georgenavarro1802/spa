#!/usr/bin/env python
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

your_djangoproject_home=os.path.split(BASE_DIR)[0]

sys.path.append(your_djangoproject_home)
os.environ['DJANGO_SETTINGS_MODULE'] = 'spa.settings'

csv_filepathname_clientes = "clientes.csv"
csv_filepathname_servicios = "servicios.csv"
csv_filepathname_productos = "productos.csv"

import django
django.setup()

from inv.models import *
from datetime import date
import csv


# dataWriter = csv.writer(open(csv_filepathname2, 'ab'), delimiter=',')
dataReader_clientes = csv.reader(open(csv_filepathname_clientes, "rU"), delimiter=',')
dataReader_servicios = csv.reader(open(csv_filepathname_servicios, "rU"), delimiter=',')
dataReader_productos = csv.reader(open(csv_filepathname_productos, "rU"), delimiter=',')


def convertirfecha(fecha):
    try:
        return date(int(fecha[6:10]), int(fecha[3:5]), int(fecha[0:2]))
    except Exception as ex:
        return datetime.now().date()


if __name__ == '__main__':

    pass

    # # Actualizar valores totales
    # ingresoprod.valor = ingresoprod.valor_compra()
    # ingresoprod.valorfob = ingresoprod.valor_fob_compra()
    # ingresoprod.save()
    #
    # print 'Fin del proceso - Compra: ' + str(ingresoprod.id)


    # Arreglar Inventarios
    # Actualizar Inventario Real
    # producto = Producto.objects.filter(codigo='MT-5-281X-2', proveedor=proveedor)[0]
    # cantidad = 4
    # costofob = 108.54
    # fob_cif = 0.30
    # cif_precio = 0.25
    # costocif = round(costofob + (costofob * fob_cif), 2)
    # valorfob = round(cantidad * costofob, 2)
    # valor = round(cantidad * costocif, 2)
    # precio = round(costocif + (costocif * cif_precio), 2)
    # if InventarioReal.objects.filter(producto=producto).exists():
    #     inventarioreal = InventarioReal.objects.filter(producto=producto)[0]
    #     inventarioreal.cantidad = cantidad
    #     inventarioreal.valor = valor
    #     inventarioreal.costo = costocif
    #     inventarioreal.costofob = costofob
    #     inventarioreal.save()
    # else:
    #     inventarioreal = InventarioReal(producto=producto,
    #                                     cantidad=cantidad,
    #                                     costo=costocif,
    #                                     costofob=costofob,
    #                                     valor=valor)
    #     inventarioreal.save()
    # print "Finalizado ajuste de inventario"

    # for row in dataReader:
    #     if not Provincia.objects.filter(nombre=row[1]).exists():
    #         provincia = Provincia()
    #         provincia.id = int(row[0])
    #         provincia.nombre = row[1]
    #         provincia.latitud = float(row[2])
    #         provincia.longitud = float(row[3])
    #         provincia.save()
    #         print provincia.id

    #
    # for row in dataReader:
    #     if not Canton.objects.filter(nombre=row[1]).exists():
    #         canton = Canton()
    #         canton.id = int(row[0])
    #         canton.nombre = row[1]
    #         canton.latitud = float(row[2])
    #         canton.longitud = float(row[3])
    #         canton.provincia = Provincia.objects.get(pk=int(row[4]))
    #         canton.save()
    #         print canton.id

    # DEPURACION DE LA BASE DE DATOS TRANSACCIONAL

    # Eliminar Proveedores
    # Proveedor.objects.all().delete()
    # print
    # "Eliminados Proveedores"
    #
    # # Eliminar Clientes
    # Cliente.objects.all().delete()
    # print
    # "Eliminados Clientes"
    #
    # # Eliminar Productos
    # Producto.objects.all().delete()
    # print
    # "Eliminados Productos"
    #
    # # Eliminar Servicios
    # Servicio.objects.all().delete()
    # print
    # "Eliminados Servicios"
    #
    # # Eliminar Receta
    # Receta.objects.all().delete()
    # print
    # "Eliminadas Recetas"
    #
    # # Eliminar Paquetes
    # Paquete.objects.all().delete()
    # print
    # "Eliminados Paquetes"
    #
    # # Eliminar Inventario
    # InventarioReal.objects.all().delete()
    # print
    # "Eliminados Inventarios"
    #
    # # Eliminar Kardex Inventario
    # KardexInventario.objects.all().delete()
    # print
    # "Eliminados Kardex Inventario"
    #
    # # Eliminar Sesiones Caja
    # SesionCaja.objects.all().delete()
    # print
    # "Eliminadas Sesiones Caja"
    #
    # # Eliminar Sesiones
    # Sesion.objects.all().delete()
    # print
    # "Eliminadas Sesiones"
    #
    # # Eliminar Paquetes
    # Paquete.objects.all().delete()
    # print
    # "Eliminados Paquetes"
    #
    # # Eliminar Ventas
    # Factura.objects.all().delete()
    # print
    # "Eliminadas Ventas"
    #
    # # Eliminar Compras
    # IngresoProducto.objects.all().delete()
    # print
    # "Eliminadas Compras"
    #
    # # Eliminar Tipo Servicio
    # TipoServicio.objects.all().delete()
    # print
    # "Eliminados Tipos Servicios"
    #
    # # Eliminar Tipo Producto
    # TipoProducto.objects.all().delete()
    # print
    # "Eliminados Tipos Productos"
    #
    # # Eliminar Pagos
    # PagoEfectivo.objects.all().delete()
    # PagoCheque.objects.all().delete()
    # PagoDeposito.objects.all().delete()
    # PagoTransferencia.objects.all().delete()
    # PagoTarjeta.objects.all().delete()
    # PagoRetencion.objects.all().delete()
    # Pago.objects.all().delete()
    # print
    # "Eliminados Pagos"
    #
    # # Eliminar Ordenes de servicio
    # OrdenServicio.objects.all().delete()
    # print
    # "Eliminados Ordenes Servicio"
    #
    # # Eliminar Solicitud Compra
    # SolicitudCompra.objects.all().delete()
    # print
    # "Eliminados Solicitud Compra"
    #
    # # Eliminar Historial precios prod
    # HistorialPrecioProducto.objects.all().delete()
    # print
    # "Eliminados Historial Precios Prod"
    #
    # # Eliminar Historial precios serv
    # HistorialPrecioServicio.objects.all().delete()
    # print
    # "Eliminados Historial Precios Serv"
    #
    # # Eliminar Historial precios serv
    # HistorialCifProducto.objects.all().delete()
    # print
    # "Eliminados Historial Precios Serv"
    #
    # # Eliminar AudiUsuarioTabla
    # AudiUsuarioTabla.objects.all().delete()
    # print
    # "Eliminados Audi Tabla"
    #
    # # IMPORTAR CLIENTES
    # linea = 1
    # for row in dataReader_clientes:
    #     if row[0] == 'N':
    #         tipo = TIPO_CLIENTE_NORMAL
    #     elif row[0] == 'C':
    #         tipo = TIPO_CLIENTE_CORPORATIVO
    #     else:
    #         tipo = TIPO_CLIENTE_VIP
    #     nombre = row[1]
    #     if not Cliente.objects.filter(tipo=tipo, nombre=nombre).exists():
    #         cliente = Cliente(tipo=tipo,
    #                           nombre=nombre,
    #                           email=row[2],
    #                           celular=row[3],
    #                           telefono=row[4],
    #                           razon_social=row[5])
    #         cliente.save()
    #         username = create_username(cliente.nombre)
    #         user = User.objects.create_user(username, cliente.email, DEFAULT_PASSWORD)
    #         user.save()
    #         cliente.usuario = user
    #         cliente.save()
    #         g = Group.objects.get(pk=CLIENTES_GROUP_ID)
    #         g.user_set.add(user)
    #         g.save()
    #         print
    #         "Cliente {} - (Lin: {})".format(cliente.id, linea)
    #
    #     linea += 1
    #
    # unidadmedida = UnidadMedida.objects.get(pk=1)
    #
    # # IMPORTAR SERVICIOS
    # if not TipoServicio.objects.filter(nombre='PELUQUERIA').exists():
    #     tipo_serv_peluqueria = TipoServicio(nombre='PELUQUERIA', codigo='01', orden=1)
    #     tipo_serv_peluqueria.save()
    # if not TipoServicio.objects.filter(nombre='SPA').exists():
    #     tipo_serv_spa = TipoServicio(nombre='SPA', codigo='02', orden=2)
    #     tipo_serv_spa.save()
    # if not TipoServicio.objects.filter(nombre='NAIL BAR').exists():
    #     tipo_serv_nailbar = TipoServicio(nombre='NAIL BAR', codigo='03', orden=3)
    #     tipo_serv_nailbar.save()
    #
    # linea = 1
    # for row in dataReader_servicios:
    #     tipo_serv = TipoServicio.objects.filter(nombre=row[0].upper())[0]
    #     codigo = row[1]
    #     descripcion = row[2]
    #     alias = row[3]
    #     precio = float(row[4])
    #     if not Servicio.objects.filter(codigo=codigo).exists():
    #         servicio = Servicio(codigo=codigo,
    #                             descripcion=descripcion,
    #                             unidadmedida=unidadmedida,
    #                             tiposervicio=tipo_serv,
    #                             alias=alias,
    #                             con_iva=True,
    #                             precio=precio)
    #         servicio.save()
    #         print
    #         "Servicio {} - (Lin: {})".format(servicio.codigo, linea)
    #
    #     linea += 1
    #
    # # IMPORTAR PRODUCTOS e INVENTARIO
    # if not TipoProducto.objects.filter(nombre='HAIR SALON').exists():
    #     tipo_prod_hairsalon = TipoProducto(nombre='HAIR SALON', codigo='01', orden=1)
    #     tipo_prod_hairsalon.save()
    # if not TipoProducto.objects.filter(nombre='SPA').exists():
    #     tipo_prod_spa = TipoProducto(nombre='SPA', codigo='02', orden=2)
    #     tipo_prod_spa.save()
    # if not TipoProducto.objects.filter(nombre='NAIL BAR').exists():
    #     tipo_prod_nailbar = TipoProducto(nombre='NAIL BAR', codigo='03', orden=3)
    #     tipo_prod_nailbar.save()
    #
    # linea = 1
    # for row in dataReader_productos:
    #     if linea > 1:
    #
    #         if row[0] == 'PV':
    #             tipodestino_tx = 'V'
    #             tipodestino = TIPO_PRODUCTO_PARA_VENTA
    #         elif row[0] == 'PC':
    #             tipodestino_tx = 'C'
    #             tipodestino = TIPO_PRODUCTO_PARA_CONSUMO
    #         else:
    #             tipodestino_tx = 'VC'
    #             tipodestino = TIPO_PRODUCTO_RECIBIDO_CONSIGNACION
    #
    #         categoria = TipoProducto.objects.filter(nombre=row[1].upper())[0]  # tipo producto es required
    #
    #         codigo = get_codigo_producto(tipodestino_tx, categoria)
    #
    #         descripcion = row[2].capitalize()
    #         marca = row[3]
    #         minimo = float(row[5])
    #         precio = float(row[7])
    #         precio_cliente_normal = float(row[7])
    #         precio_cliente_corporativo = float(row[8])
    #         precio_cliente_vip = float(row[9])
    #         alias = descripcion[:20].lower()
    #
    #         producto = Producto(tipo=tipodestino,
    #                             codigo=codigo,
    #                             descripcion=descripcion,
    #                             unidadmedida=unidadmedida,
    #                             tipoproducto=categoria,
    #                             marca=marca,
    #                             minimo=minimo,
    #                             precio=precio,
    #                             precio_cliente_normal=precio_cliente_normal,
    #                             precio_cliente_corporativo=precio_cliente_corporativo,
    #                             precio_cliente_vip=precio_cliente_vip)
    #         producto.save()
    #
    #         # Cantidad y Costo para Inventario inicial
    #         cantidad = float(row[4])
    #         costo = float(row[6])
    #         valor = round(cantidad * costo, 2)
    #         area = Area.objects.get(pk=1)
    #
    #         # Actualizar Inventario Real
    #         if not InventarioReal.objects.filter(producto=producto).exists():
    #             inventarioreal = InventarioReal(producto=producto,
    #                                             cantidad=cantidad,
    #                                             costo=costo,
    #                                             valor=valor,
    #                                             area=area)
    #         else:
    #             inventarioreal = InventarioReal.objects.filter(producto=producto)[0]
    #             inventarioreal.cantidad = cantidad
    #             inventarioreal.costo = costo
    #             inventarioreal.valor = valor
    #             inventarioreal.area = area
    #
    #         inventarioreal.save()
    #
    #         print
    #         "Inventario {} Producto {} - (Lin: {})".format(inventarioreal.id, producto.codigo, linea)
    #
    #     linea += 1