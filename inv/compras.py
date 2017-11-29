import json

import xlrd
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render_to_response

from inv.forms import IngresoProductoForm, DetalleIngresoProductoForm, ProveedorForm, ImportarArchivoXLSForm
from inv.funciones import salva_auditoria, generar_nombre, ok_json, bad_json
from inv.models import *
from inv.views import addUserData, convertir_fecha
from spa.settings import ACCION_ADICIONAR


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    data = {'title': 'Compras'}
    addUserData(request, data)
    usuario = request.user

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'ingresoinv':
            try:
                datos = json.loads(request.POST['datos'])
                with transaction.atomic():
                    ingresoprod = IngresoProducto(proveedor_id=int(datos['proveedor']),
                                                  tipodocumento_id=int(datos['tipodocumento']),
                                                  numerodocumento=datos['numerodocumento'],
                                                  fechadocumento=convertir_fecha(datos['fechadocumento']),
                                                  descripcion=datos['descripcion'],
                                                  fecha=datetime.now().date(),
                                                  usuario=usuario)
                    ingresoprod.save()
                    # items
                    items = datos['items']
                    for d in items:
                        codigo = d['codigo']
                        if Producto.objects.filter(codigo=codigo).exists():
                            producto = Producto.objects.filter(codigo=codigo)[0]
                        else:
                            return HttpResponse(json.dumps({"result": "bad", "mensaje": "El producto no existe"}), content_type="application/json")

                        detalleingprod = DetalleIngresoProducto(compra=ingresoprod,
                                                                producto=producto,
                                                                cantidad=float(d['cantidad']),
                                                                costo=float(d['costo']),
                                                                valor=float(d['valor']))
                        detalleingprod.save()

                        # Guardar Historial de costos CIF
                        historialcif = HistorialCifProducto(producto=producto,
                                                            compra=ingresoprod,
                                                            cif=detalleingprod.costo,
                                                            usuario=request.user)
                        historialcif.save()

                        # Actualizar Inventario Real
                        if Area.objects.exists():
                            if Area.objects.filter(es_principal=True):
                                area = Area.objects.filter(es_principal=True)[0]
                            else:
                                area = Area.objects.all()[0]
                        else:
                            area = Area(nombre='Matriz', es_principal=True)
                            area.save()

                        # COSTO Y SALDO ANTES DEL MOVIMIENTO
                        saldoinicialvalor = detalleingprod.producto.valor_inventario(area)
                        saldoinicialcantidad = detalleingprod.producto.stock_inventario(area)

                        # ACTUALIZAR INVENTARIO REAL
                        costoproducto = round((detalleingprod.valor / detalleingprod.cantidad), 2) if detalleingprod.cantidad else 0
                        producto.actualizar_inventario_ingreso(costoproducto, detalleingprod.cantidad, area)
                        inventario = producto.mi_inventario(area)

                        # ACTUALIZAR KARDEX
                        kardex = KardexInventario(producto=detalleingprod.producto,
                                                  inventario=inventario,
                                                  tipomovimiento=TIPO_MOVIMIENTO_ENTRADA,
                                                  dcompra=detalleingprod,
                                                  saldoinicialvalor=saldoinicialvalor,
                                                  saldoinicialcantidad=saldoinicialcantidad,
                                                  cantidad=detalleingprod.cantidad,
                                                  costo=costoproducto,
                                                  valor=round((costoproducto * detalleingprod.cantidad), 2))
                        kardex.save()

                        # COSTO Y SALDO DESPUES DEL MOVIMIENTO
                        saldofinalvalor = detalleingprod.producto.valor_inventario(area)
                        saldofinalcantidad = detalleingprod.producto.stock_inventario(area)
                        kardex.saldofinalcantidad = saldofinalcantidad
                        kardex.saldofinalvalor = saldofinalvalor
                        kardex.save()

                    # Actualizar valore total de la compra
                    ingresoprod.valor = ingresoprod.valor_compra()
                    ingresoprod.save()
                    salva_auditoria(request, ingresoprod, ACCION_ADICIONAR)
                    return ok_json()

            except Exception:
                return bad_json(error=1)

        elif action == 'chequeacodigos':
            cod_existen = [x.codigo for x in Producto.objects.filter(codigo__in=request.POST['codigos'].split(","))]
            if cod_existen:
                return ok_json(data={"codigosexisten": cod_existen})
            return bad_json(error=1)

        elif action == 'comprobarnumero':
            proveedor = Proveedor.objects.get(pk=request.POST['pid'])
            numero = request.POST['numero']
            tipodoc = TipoDocumento.objects.get(pk=request.POST['tipodoc'])
            if proveedor.ingresoproducto_set.filter(numerodocumento=numero, tipodocumento=tipodoc).exists():
                return bad_json(error=1)
            return ok_json()

        elif action == 'importar':
            form = ImportarArchivoXLSForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    nfile = request.FILES['archivo']
                    nfile._name = generar_nombre("importacion_", nfile._name)
                    archivo = Archivo(nombre='IMPORTACION DE PRODUCTOS',
                                      fecha=datetime.now(),
                                      archivo=nfile)
                    archivo.save()

                    ingresoprod = IngresoProducto(proveedor=Proveedor.objects.get(pk=request.POST['proveedor']),
                                                  tipodocumento_id=1,   # factura
                                                  numerodocumento='111-111-111111',
                                                  fechadocumento=datetime.today(),
                                                  descripcion='MIGRACION',
                                                  fecha=datetime.today(),
                                                  usuario=usuario)
                    ingresoprod.save()

                    # 0 - Codigo
                    # 1 - Descripcion
                    # 2 - Categoria producto
                    # 3 - Codigo barra
                    # 4 - Cantidad minima
                    # 5 - Precio referencial
                    # 6 - Precio cliente normal
                    # 7 - Precio cliente corporativo
                    # 8 - Precio cliente vip
                    # 9 - Cantidad Existencia
                    # 10 - Costo unitario
                    workbook = xlrd.open_workbook(archivo.archivo.file.name)
                    sheet = workbook.sheet_by_index(0)
                    linea = 1
                    for rowx in range(sheet.nrows):
                        try:
                            cols = sheet.row_values(rowx)

                            codigo = cols[0]
                            descripcion = cols[1]
                            categoria = TipoProducto.objects.filter(codigo=cols[2])[0] if cols[2] else ""
                            codigobarra = cols[3]
                            cantidadminima = cols[4]
                            precio_referencial = cols[5]
                            precio_cliente_normal = cols[6]
                            precio_cliente_corporativo = cols[7]
                            precio_cliente_vip = cols[8]
                            cantidad = float(cols[9])
                            costo = float(cols[10])
                            valor = round(cantidad * costo, 2)

                            if codigo and Producto.objects.filter(codigo=codigo).exists():
                                producto = Producto.objects.filter(codigo=codigo)[0]
                            else:
                                codigo = "PV-{}-0001".format(categoria.codigo)
                                ultimo_producto = categoria.get_ultimo_producto()
                                if ultimo_producto:
                                    codigo = "PV-{}-{}".format(categoria.codigo, str(ultimo_producto.secuencia_codigo() + 1).zfill(4))
                                producto = Producto(codigo=codigo,
                                                    descripcion=descripcion,
                                                    unidadmedida_id=1,
                                                    tipoproducto=categoria,
                                                    alias=descripcion[:25],
                                                    codigobarra=codigobarra,
                                                    minimo=cantidadminima,
                                                    precio=precio_referencial,
                                                    precio_cliente_normal=precio_cliente_normal,
                                                    precio_cliente_corporativo=precio_cliente_corporativo,
                                                    precio_cliente_vip=precio_cliente_vip)
                                producto.save()

                            detalleingprod = DetalleIngresoProducto(compra=ingresoprod,
                                                                    producto=producto,
                                                                    cantidad=cantidad,
                                                                    costo=costo,
                                                                    valor=valor)
                            detalleingprod.save()

                            # Guardar Historial de costos CIF
                            historialcif = HistorialCifProducto(producto=producto,
                                                                compra=ingresoprod,
                                                                cif=detalleingprod.costo,
                                                                usuario=request.user)
                            historialcif.save()

                            # Actualizar Inventario Real
                            if Area.objects.exists():
                                if Area.objects.filter(es_principal=True):
                                    area = Area.objects.filter(es_principal=True)[0]
                                else:
                                    area = Area.objects.all()[0]
                            else:
                                area = Area(nombre='Matriz', es_principal=True)
                                area.save()

                            # COSTO Y SALDO ANTES DEL MOVIMIENTO
                            saldoinicialvalor = detalleingprod.producto.valor_inventario(area)
                            saldoinicialcantidad = detalleingprod.producto.stock_inventario(area)

                            # ACTUALIZAR INVENTARIO REAL
                            costoproducto = round((detalleingprod.valor / detalleingprod.cantidad), 2) if detalleingprod.cantidad else 0
                            producto.actualizar_inventario_ingreso(costoproducto, detalleingprod.cantidad, area)
                            inventario = producto.mi_inventario(area)

                            # ACTUALIZAR KARDEX
                            kardex = KardexInventario(producto=detalleingprod.producto,
                                                      inventario=inventario,
                                                      tipomovimiento=TIPO_MOVIMIENTO_ENTRADA,
                                                      dcompra=detalleingprod,
                                                      saldoinicialvalor=saldoinicialvalor,
                                                      saldoinicialcantidad=saldoinicialcantidad,
                                                      cantidad=detalleingprod.cantidad,
                                                      costo=costoproducto,
                                                      valor=round(costoproducto * detalleingprod.cantidad, 2))
                            kardex.save()

                            # COSTO Y SALDO DESPUES DEL MOVIMIENTO
                            saldofinalvalor = detalleingprod.producto.valor_inventario(area)
                            saldofinalcantidad = detalleingprod.producto.stock_inventario(area)
                            kardex.saldofinalcantidad = saldofinalcantidad
                            kardex.saldofinalvalor = saldofinalvalor
                            kardex.save()

                            # Actualizar valore total de la compra
                            ingresoprod.valor = ingresoprod.valor_compra()
                            ingresoprod.save()
                            salva_auditoria(request, ingresoprod, ACCION_ADICIONAR)

                            linea += 1
                        except Exception:
                            return bad_json(mensaje=u'Error al ingresar la linea: %s' % linea)

                    return ok_json()
                except Exception:
                    return bad_json(error=1)

        return bad_json(error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'importar':
                try:
                    data['title'] = u'Importación de inventario'
                    data['form'] = ImportarArchivoXLSForm()
                    return render_to_response("compras/importar.html", data)

                except Exception:
                    pass

        else:
            data['form'] = IngresoProductoForm(initial={'fechadocumento': datetime.now().date()})
            data['form2'] = DetalleIngresoProductoForm()
            data['form_entidad'] = ProveedorForm(prefix='proveedor')
            data['valor_iva'] = data['iva']
            return render_to_response("compras/view.html", data)
