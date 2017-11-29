from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from inv.funciones import MESES_CHOICES, url_back, mensaje_excepcion
from inv.funciones_estadisticas import (valores_ventas_total_fechas, cantidad_facturas_fechas,
                                        valores_ventas_subtotal_fechas, valores_ventas_iva_fechas, pagos_total_fechas,
                                        pagos_efectivo_fechas, pagos_cheque_fechas, pagos_deposito_fechas,
                                        pagos_transferencia_fechas, pagos_tarjeta_fechas, pagos_retencion_fechas,
                                        cantidad_facturas_pagos_efectivo_fechas, cantidad_facturas_pagos_cheque_fechas,
                                        cantidad_facturas_pagos_deposito_fechas,
                                        cantidad_facturas_pagos_transferencia_fechas,
                                        cantidad_facturas_pagos_tarjeta_fechas,
                                        cantidad_facturas_pagos_retencion_fechas, cantidad_facturas_pagos_total_fechas,
                                        valores_ventas_total_mes_anio, cantidad_facturas_mes_anio,
                                        valores_ventas_subtotal_mes_anio, valores_ventas_iva_mes_anio,
                                        pagos_total_mes_anio)
from inv.models import Producto, TipoProducto, Vendedor, Cliente, Proveedor
from inv.views import addUserData, convertir_fecha


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': u'Estadísticas'}
    addUserData(request, data)
    data['mes'] = MESES_CHOICES[datetime.now().month - 1][1]
    data['anio'] = anio = datetime.now().year

    inicio = datetime(anio, 1, 1, 0, 0, 0)
    fin = datetime(anio, 12, 31, 0, 0, 0)
    if 'inicio' in request.GET:
        inicio = convertir_fecha(request.GET['inicio'])
    if 'fin' in request.GET:
        fin = convertir_fecha(request.GET['fin'])
    data['inicio'] = inicio
    data['fin'] = fin

    if 'action' in request.GET:
        action = request.GET['action']

        if action == 'ventas_totales':
            try:
                data['title1'] = 'Valores Ventas ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                    fin.strftime('%d-%m-%Y'))
                data['title2'] = 'Cantidad Facturas ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                       fin.strftime('%d-%m-%Y'))
                data['title3'] = 'Resumen Ventas ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                    fin.strftime('%d-%m-%Y'))
                valores_totales = []
                cantidad_facturas = []
                valores_tabla = []
                for i in range(inicio.month, fin.month+1):
                    valores_totales.append(valores_ventas_total_mes_anio(i, inicio.year))
                    cantidad_facturas.append(cantidad_facturas_mes_anio(i, inicio.year))
                    valores_tabla.append((MESES_CHOICES[i - 1][1],
                                          cantidad_facturas_mes_anio(i, inicio.year),
                                          valores_ventas_subtotal_mes_anio(i, inicio.year),
                                          valores_ventas_iva_mes_anio(i, inicio.year),
                                          valores_ventas_total_mes_anio(i, inicio.year)))
                data['valores_totales'] = valores_totales
                data['cantidad_facturas'] = cantidad_facturas
                data['valores_tabla'] = valores_tabla
                # Totales del anio
                data['cantidad_facturas_fechas'] = cantidad_facturas_fechas(inicio, fin)
                data['valores_ventas_subtotal_fechas'] = valores_ventas_subtotal_fechas(inicio, fin)
                data['valores_ventas_iva_fechas'] = valores_ventas_iva_fechas(inicio, fin)
                data['valores_ventas_total_fechas'] = valores_ventas_total_fechas(inicio, fin)
                return render_to_response("estadisticas/ventas_totales.html", data)
            except Exception as ex:
                pass

        elif action == 'pagos_totales':
            try:
                data['title1'] = 'Pagos ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                           fin.strftime('%d-%m-%Y'))
                data['title2'] = 'Formas de Pagos ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                     fin.strftime('%d-%m-%Y'))
                data['title3'] = 'Pagos por formas de pago ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                              fin.strftime('%d-%m-%Y'))

                pagos_totales = []
                valores_tabla = []
                meses = []
                # Grafico 1
                for i in range(inicio.month, fin.month+1):
                    pagos_totales.append(pagos_total_mes_anio(i, inicio.year))
                    meses.append(MESES_CHOICES[i - 1][1])
                data['pagos_totales'] = pagos_totales
                data['meses'] = meses

                # Grafico 2
                data['pagos_efectivo_anio'] = pagos_efectivo_fechas(inicio, fin)
                data['pagos_cheque_anio'] = pagos_cheque_fechas(inicio, fin)
                data['pagos_deposito_anio'] = pagos_deposito_fechas(inicio, fin)
                data['pagos_transferencia_anio'] = pagos_transferencia_fechas(inicio, fin)
                data['pagos_tarjeta_anio'] = pagos_tarjeta_fechas(inicio, fin)
                data['pagos_retencion_anio'] = pagos_retencion_fechas(inicio, fin)

                # Tabla
                valores_tabla.append(('Efectivo',
                                      cantidad_facturas_pagos_efectivo_fechas(inicio, fin),
                                      pagos_efectivo_fechas(inicio, fin)))
                valores_tabla.append(('Cheque',
                                      cantidad_facturas_pagos_cheque_fechas(inicio, fin),
                                      pagos_cheque_fechas(inicio, fin)))
                valores_tabla.append(('Deposito',
                                      cantidad_facturas_pagos_deposito_fechas(inicio, fin),
                                      pagos_deposito_fechas(inicio, fin)))
                valores_tabla.append(('Transferencia',
                                      cantidad_facturas_pagos_transferencia_fechas(inicio, fin),
                                      pagos_transferencia_fechas(inicio, fin)))
                valores_tabla.append(('Tarjeta',
                                      cantidad_facturas_pagos_tarjeta_fechas(inicio, fin),
                                      pagos_tarjeta_fechas(inicio, fin)))
                valores_tabla.append(('Retencion',
                                      cantidad_facturas_pagos_retencion_fechas(inicio, fin),
                                      pagos_retencion_fechas(inicio, fin)))
                data['valores_tabla'] = valores_tabla
                data['cantidad_facturas_pagos_total_anio'] = cantidad_facturas_pagos_total_fechas(inicio, fin)
                data['pagos_total_anio'] = pagos_total_fechas(inicio, fin)
                return render_to_response("estadisticas/pagos_totales.html", data)
            except Exception as ex:
                pass

        elif action == 'productos_mas_vendidos':
            try:
                data['title1'] = 'Productos mas vendidos ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                            fin.strftime('%d-%m-%Y'))
                data['title2'] = 'Tabla Top Ten Productos ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                             fin.strftime('%d-%m-%Y'))
                # Grafico 1 y Tabla
                topten = []
                for producto in Producto.objects.filter(detallefactura__isnull=False,
                                                        detallefactura__factura__fecha__range=(inicio, fin)).\
                        distinct().annotate(cantventas=Count('detallefactura__id')).order_by('-cantventas')[:10]:
                    topten.append((producto, producto.cantventas, producto.valor_ventas()))
                data['topten'] = topten
                return render_to_response("estadisticas/productos_mas_vendidos.html", data)
            except Exception as ex:
                pass

        elif action == 'categorias_mas_vendidas':
            try:
                data['title1'] = 'Categorias mas vendidos ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                             fin.strftime('%d-%m-%Y'))
                data['title2'] = 'Tabla Top Ten Categorias ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                              fin.strftime('%d-%m-%Y'))
                # Grafico 1 y Tabla
                topten = []
                for categoria in TipoProducto.objects.filter(producto__detallefactura__factura__fecha__range=(inicio, fin)).annotate(
                        cantventas=Count('producto__detallefactura__id')).distinct().order_by('-cantventas')[:10]:
                    topten.append((categoria, categoria.cantventas, categoria.valor_ventas()))
                data['topten'] = topten
                return render_to_response("estadisticas/categorias_mas_vendidas.html", data)
            except Exception as ex:
                pass

        elif action == 'vendedores_mas_venden':
            try:
                data['title1'] = 'Vendedores que mas venden ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                               fin.strftime('%d-%m-%Y'))
                data['title2'] = 'Vendedores que mas venden ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                               fin.strftime('%d-%m-%Y'))
                data['title3'] = 'Ranking Vendedores ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                        fin.strftime('%d-%m-%Y'))

                topten = []
                for vendedor in Vendedor.objects.filter(factura__isnull=False, factura__valida=True,
                                                        factura__fecha__range=(inicio, fin)).distinct().annotate(
                        cantventas=Count('factura__id')).distinct().order_by('-cantventas')[:10]:
                    topten.append((vendedor.usuario.username, vendedor.cantventas, vendedor.valor_ventas()))
                data['topten'] = topten
                return render_to_response("estadisticas/vendedores_mas_venden.html", data)
            except Exception as ex:
                pass

        elif action == 'vendedores_mas_comisionan':
            try:
                data['title1'] = 'Vendedores mas comisionan ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                               fin.strftime('%d-%m-%Y'))
                data['title2'] = 'Vendedores mas comisionan ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                               fin.strftime('%d-%m-%Y'))
                data['title3'] = 'Ranking Vendedores ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                        fin.strftime('%d-%m-%Y'))

                topten = []
                for vendedor in Vendedor.objects.filter(factura__isnull=False, factura__valida=True,
                                                        factura__fecha__range=(inicio, fin)).distinct().annotate(
                        cantventas=Count('factura__id')).distinct().order_by('-cantventas')[:10]:
                    topten.append((vendedor.usuario.username, vendedor.cantventas, vendedor.comision_ventas()))
                data['topten'] = topten
                return render_to_response("estadisticas/vendedores_mas_comisionan.html", data)
            except Exception as ex:
                pass

        elif action == 'vendedores_mas_cobran':
            try:
                data['title1'] = 'Vendedores que mas cobran ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                               fin.strftime('%d-%m-%Y'))
                data['title2'] = 'Vendedores que mas cobran ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                               fin.strftime('%d-%m-%Y'))
                data['title3'] = 'Ranking Vendedores ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                        fin.strftime('%d-%m-%Y'))

                topten = []
                for vendedor in Vendedor.objects.filter(factura__valida=True, factura__pago__isnull=False,
                                                        factura__fecha__range=(inicio, fin)).distinct().annotate(
                        valorpagos=Sum('factura__pago__valor')).distinct().order_by('-valorpagos')[:10]:
                    topten.append((vendedor.usuario.username, vendedor.valorpagos))
                data['topten'] = topten
                return render_to_response("estadisticas/vendedores_mas_cobran.html", data)
            except Exception as ex:
                pass

        elif action == 'clientes_mas_compran':
            try:
                data['title1'] = 'Clientes que mas compran ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                              fin.strftime('%d-%m-%Y'))
                data['title2'] = 'Clientes que mas compran ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                              fin.strftime('%d-%m-%Y'))
                data['title3'] = 'Ranking Clientes ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                      fin.strftime('%d-%m-%Y'))

                topten = []
                for cliente in Cliente.objects.filter(factura__isnull=False, factura__valida=True,
                                                      factura__fecha__range=(inicio, fin)).distinct().annotate(
                        cantventas=Count('factura__id')).distinct().order_by('-cantventas')[:10]:
                    topten.append((cliente, cliente.cantventas, cliente.valor_ventas()))
                data['topten'] = topten
                return render_to_response("estadisticas/clientes_mas_compran.html", data)
            except Exception as ex:
                pass

        elif action == 'proveedores_mas_compran':
            try:
                data['title1'] = 'Proveedores que mas se les compra ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                                       fin.strftime('%d-%m-%Y'))
                data['title2'] = 'Proveedores que mas se les compra ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                                       fin.strftime('%d-%m-%Y'))
                data['title3'] = 'Ranking Proveedores ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                         fin.strftime('%d-%m-%Y'))

                topten = []
                for proveedor in Proveedor.objects.filter(ingresoproducto__isnull=False,
                                                          ingresoproducto__fecha__range=(inicio, fin)).distinct().\
                        annotate(cantcompras=Count('ingresoproducto__id')).distinct().order_by('-cantcompras')[:10]:
                    topten.append((proveedor, proveedor.cantcompras, proveedor.valor_compras()))
                data['topten'] = topten
                return render_to_response("estadisticas/proveedores_mas_compran.html", data)
            except Exception as ex:
                pass

        elif action == 'resumen_general_por_proveedores':
            try:
                data['title1'] = 'Gráfico de ganancias ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                          fin.strftime('%d-%m-%Y'))
                data['title2'] = 'Resumen financiero por proveedores ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                                        fin.strftime('%d-%m-%Y'))
                valores_tabla = []
                valor_total_cif_compras = 0
                valor_total_productos_comision_ventas = 0
                valor_total_productos_pagos_retencion = 0
                valor_total_productos_ventas = 0
                ganancia_total = 0
                for proveedor in Proveedor.objects.filter(ingresoproducto__isnull=False):
                    # Valores por proveedor
                    valor_cif_compras = proveedor.valor_compras_fechas(inicio, fin)
                    valor_productos_comision_ventas = proveedor.valor_productos_comision_ventas_fechas(inicio, fin)
                    valor_productos_pagos_retencion = proveedor.valor_productos_pagos_retencion_fechas(inicio, fin)
                    valor_productos_ventas = proveedor.valor_productos_ventas_fechas(inicio, fin)
                    ganancia = valor_productos_ventas - (valor_cif_compras +
                                                         valor_productos_comision_ventas +
                                                         valor_productos_pagos_retencion)
                    # Valores totales
                    valor_total_cif_compras += valor_cif_compras
                    valor_total_productos_comision_ventas += valor_productos_comision_ventas
                    valor_total_productos_pagos_retencion += valor_productos_pagos_retencion
                    valor_total_productos_ventas += valor_productos_ventas
                    ganancia_total += ganancia

                    valores_tabla.append((proveedor.nombre_simple(),
                                          valor_cif_compras,
                                          valor_productos_comision_ventas,
                                          valor_productos_pagos_retencion,
                                          valor_productos_ventas,
                                          ganancia))

                data['valores_tabla'] = valores_tabla
                data['valor_total_cif_compras'] = valor_total_cif_compras
                data['valor_total_productos_comision_ventas'] = valor_total_productos_comision_ventas
                data['valor_total_productos_pagos_retencion'] = valor_total_productos_pagos_retencion
                data['valor_total_productos_ventas'] = valor_total_productos_ventas
                data['ganancia_total'] = ganancia_total
                data['proveedores'] = Proveedor.objects.all()
                return render_to_response("estadisticas/resumen_general_por_proveedores.html", data)
            except Exception as ex:
                pass

        elif action == 'resumen_general_por_vendedores':
            try:
                data['title1'] = 'Valores Facturados ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                        fin.strftime('%d-%m-%Y'))
                data['title2'] = 'Valores Cobrados ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                      fin.strftime('%d-%m-%Y'))
                data['title3'] = 'Valores Pendientes ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                        fin.strftime('%d-%m-%Y'))
                data['title4'] = 'Resumen general por vendedores ({} al {})'.format(inicio.strftime('%d-%m-%Y'),
                                                                                    fin.strftime('%d-%m-%Y'))

                lista_vendedores = []
                for vendedor in Vendedor.objects.filter(factura__isnull=False,
                                                        factura__valida=True,
                                                        factura__fecha__range=(inicio, fin)).distinct():
                    lista_vendedores.append((vendedor.usuario.username,
                                             vendedor.valor_ventas(),
                                             vendedor.valor_pagos(),
                                             vendedor.valor_pendiente(),
                                             vendedor.nombre))
                data['lista_vendedores'] = lista_vendedores

                return render_to_response("estadisticas/resumen_general_por_vendedores.html", data)
            except Exception as ex:
                pass

        return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

    else:
        return render_to_response("estadisticas/view.html", data)
