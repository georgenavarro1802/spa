import collections
import math
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string

from inv.forms import ProductoForm, FotoProductoForm
from inv.funciones import (salva_auditoria, MiPaginador, generar_nombre, url_back, mensaje_excepcion, generar_pdf,
                           ok_json, bad_json)
from inv.models import Producto, TipoProducto, HistorialPrecioProducto
from inv.views import addUserData
from spa.settings import (ACCION_ADICIONAR, ACCION_MODIFICAR, ACCION_ELIMINAR, TIPO_PRODUCTO_PARA_VENTA,
                          TIPO_PRODUCTO_PARA_CONSUMO)


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': u'Productos'}
    addUserData(request, data)

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            f = ProductoForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        producto = Producto(tipo=f.cleaned_data['tipo'],
                                            codigo=f.cleaned_data['codigo'],
                                            descripcion=f.cleaned_data['descripcion'],
                                            unidadmedida=f.cleaned_data['unidadmedida'],
                                            tipoproducto=f.cleaned_data['tipoproducto'],
                                            alias=f.cleaned_data['alias'],
                                            codigobarra=f.cleaned_data['codigobarra'],
                                            minimo=f.cleaned_data['minimo'],
                                            con_iva=f.cleaned_data['con_iva'],
                                            precio=f.cleaned_data['precio'],
                                            precio_cliente_normal=f.cleaned_data['precio_cliente_normal'],
                                            precio_cliente_corporativo=f.cleaned_data['precio_cliente_corporativo'],
                                            precio_cliente_vip=f.cleaned_data['precio_cliente_vip'])
                        producto.save()

                        # Guardar Historial de cambios de precios
                        historialprecio = HistorialPrecioProducto(producto=producto,
                                                                  precio=producto.precio,
                                                                  precio_cliente_normal=producto.precio_cliente_normal,
                                                                  precio_cliente_corporativo=producto.precio_cliente_corporativo,
                                                                  precio_cliente_vip=producto.precio_cliente_vip,
                                                                  usuario=request.user,
                                                                  modulo='P',  # C - Compra, P - Productos
                                                                  accion=ACCION_ADICIONAR)
                        historialprecio.save()

                        salva_auditoria(request, producto, ACCION_ADICIONAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'edit':
            producto = Producto.objects.get(pk=request.POST['id'])
            f = ProductoForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        flag1 = producto.precio != f.cleaned_data['precio']
                        flag2 = producto.precio_cliente_normal != f.cleaned_data['precio_cliente_normal']
                        flag3 = producto.precio_cliente_corporativo != f.cleaned_data['precio_cliente_corporativo']
                        flag4 = producto.precio_cliente_vip != f.cleaned_data['precio_cliente_vip']
                        producto.codigo = f.cleaned_data['codigo']
                        producto.codigobarra = f.cleaned_data['codigobarra']
                        producto.descripcion = f.cleaned_data['descripcion']
                        producto.tipoproducto = f.cleaned_data['tipoproducto']
                        producto.unidadmedida = f.cleaned_data['unidadmedida']
                        producto.alias = f.cleaned_data['alias']
                        producto.minimo = f.cleaned_data['minimo']
                        producto.con_iva = f.cleaned_data['con_iva']
                        producto.precio = f.cleaned_data['precio']
                        producto.precio_cliente_normal = f.cleaned_data['precio_cliente_normal']
                        producto.precio_cliente_corporativo = f.cleaned_data['precio_cliente_corporativo']
                        producto.precio_cliente_vip = f.cleaned_data['precio_cliente_vip']
                        producto.save()

                        # Guardar Historial si hubo cambios de precios
                        if flag1 or flag2 or flag3 or flag4:
                            historialprecio = HistorialPrecioProducto(producto=producto,
                                                                      precio=producto.precio,
                                                                      precio_cliente_normal=producto.precio_cliente_normal,
                                                                      precio_cliente_corporativo=producto.precio_cliente_corporativo,
                                                                      precio_cliente_vip=producto.precio_cliente_vip,
                                                                      fecha=datetime.now().date(),
                                                                      usuario=request.user,
                                                                      modulo='P',
                                                                      accion=ACCION_MODIFICAR)
                            historialprecio.save()

                        for pp in producto.paqueteproducto_set.all():
                            pp.paquete.save()

                        salva_auditoria(request, producto, ACCION_MODIFICAR)
                    return ok_json()

                except Exception:
                    return bad_json(error=2)
            else:
                return bad_json(error=2)

        elif action == 'delete':
            producto = Producto.objects.get(pk=request.POST['id'])
            try:
                with transaction.atomic():
                    salva_auditoria(request, producto, ACCION_ELIMINAR)
                    producto.delete()
                return ok_json()
            except Exception:
                return bad_json(error=3)

        elif action == 'get_next_codigo':
            t = int(request.POST['tid'])
            if t == TIPO_PRODUCTO_PARA_VENTA:
                tipo = 'V'
            elif t == TIPO_PRODUCTO_PARA_CONSUMO:
                tipo = 'C'
            else:
                tipo = 'R'
            categoria = TipoProducto.objects.get(pk=request.POST['cid'])
            try:
                codigo = "P{}-{}-0001".format(tipo, categoria.codigo)
                ultimo_producto = categoria.get_ultimo_producto()
                if ultimo_producto:
                    codigo = "P{}-{}-{}".format(tipo, categoria.codigo, str(ultimo_producto.secuencia_codigo() + 1).zfill(4))
                return ok_json(data={"codigo": codigo})
            except Exception:
                return bad_json(error=1)

        elif action == 'cargarfoto':
            form = FotoProductoForm(request.POST, request.FILES)
            producto = Producto.objects.get(pk=request.POST['id'])
            if form.is_valid():
                try:
                    with transaction.atomic():
                        newfile = request.FILES['foto']
                        newfile._name = generar_nombre("foto_", newfile._name)
                        producto.foto = newfile
                        producto.save()
                    return ok_json()
                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'favorito':
            try:
                producto = Producto.objects.get(pk=request.POST['idprod'])
                try:
                    with transaction.atomic():
                        producto.favorito = False if producto.favorito else True
                        producto.save()
                        return ok_json()
                except Exception:
                    return bad_json(error=1)
            except:
                return bad_json(error=1)

        return bad_json(error=0)

    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    data['title'] = u'Crear Producto'
                    data['form'] = ProductoForm()
                    return render_to_response('productos/add.html', data)
                except Exception as ex:
                    pass

            elif action == 'edit':
                try:
                    data['title'] = u'Modificar Producto'
                    data['producto'] = producto = Producto.objects.get(pk=request.GET['id'])
                    form = ProductoForm(initial=model_to_dict(producto))
                    form.for_editproducto()
                    data['form'] = form
                    return render_to_response('productos/edit.html', data)
                except Exception as ex:
                    pass

            elif action == 'delete':
                try:
                    data['title'] = u'Eliminar Producto'
                    data['producto'] = Producto.objects.get(pk=request.GET['id'])
                    return render_to_response('productos/delete.html', data)
                except Exception as ex:
                    pass

            elif action == 'cargarfoto':
                try:
                    data['title'] = u'Cargar Foto del Producto '
                    data['producto'] = Producto.objects.get(pk=request.GET['id'])
                    data['form'] = FotoProductoForm()
                    return render_to_response('productos/cargarfoto.html', data)
                except Exception as ex:
                    pass

            elif action == 'catalogo':
                try:
                    data['title'] = u'Catalogo de Productos'
                    data['categorias'] = categorias = TipoProducto.objects.all()
                    categoria = categorias[0]
                    if 'cid' in request.GET:
                        cid = int(request.GET['cid'])
                        categoria = categorias.filter(pk=cid)[0]
                    inventarios = categoria.productos_con_existencias()

                    cantidad_filas = 0
                    if inventarios:
                        if inventarios.count() > 8:
                            cantidad_filas = int(math.ceil(inventarios.count() / 8.0))
                        else:
                            cantidad_filas = 1
                    salto = 8
                    lista = []
                    for i in range(cantidad_filas):
                        a = i * salto
                        lista.append((i, inventarios[a:(a + salto)]))

                    data['lista'] = lista
                    data['cantidad_filas'] = cantidad_filas
                    data['categoria'] = categoria
                    return render_to_response('productos/catalogo.html', data)
                except Exception as ex:
                    pass

            elif action == 'catalogopdf':
                try:
                    data['title'] = u'Catálogo de Productos por Categoria'
                    categoria = TipoProducto.objects.get(pk=int(request.GET['cid']))

                    inventarios = categoria.productos_con_existencias()
                    cantidad_productos = inventarios.count()
                    cantidad_paginas = int(math.ceil(cantidad_productos / 12.0))

                    paginas = []
                    salto = 4
                    inicio = 0
                    fin = 4
                    for p in range(1, cantidad_paginas + 1):
                        grupo1 = inventarios[inicio:fin]
                        inicio = fin
                        fin += salto
                        grupo2 = inventarios[inicio:fin]
                        inicio = fin
                        fin += salto
                        grupo3 = inventarios[inicio:fin]
                        inicio = fin
                        fin += salto
                        paginas.append((p, grupo1, grupo2, grupo3))

                    data['paginas'] = paginas
                    data['categoria'] = categoria
                    data['request'] = request
                    html = render_to_string('productos/catalogopdf.html', data, request)
                    return generar_pdf(html)
                except Exception as ex:
                    pass

            elif action == 'todospdf':
                try:
                    data['title'] = u'Catálogo de todos los Productos'
                    data['categorias'] = categorias = TipoProducto.objects.filter(producto__inventarioreal__cantidad__gt=0).distinct()

                    lista = collections.OrderedDict()
                    listado_final = collections.OrderedDict()
                    for c in categorias:
                        lista_productos_ordenados = []
                        for inventario in c.productos_con_existencias():
                            lista_productos_ordenados.append(inventario)
                        lista[c] = lista_productos_ordenados

                    salto = 4
                    for x, y in lista.items():
                        inicio = 0
                        fin = 4
                        listado = []
                        for p in range(1, x.cantidad_paginas_catalogo() + 1):
                            grupo1 = y[inicio:fin]
                            inicio = fin
                            fin += salto
                            grupo2 = y[inicio:fin]
                            inicio = fin
                            fin += salto
                            grupo3 = y[inicio:fin]
                            inicio = fin
                            fin += salto
                            listado.append((p, grupo1, grupo2, grupo3))
                        listado_final[x] = listado

                    data['listado_final'] = listado_final
                    data['request'] = request
                    html = render_to_string('productos/todospdf.html', data, request)
                    return generar_pdf(html)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:
            search = None
            tipo = None
            tipodestino = None

            if 't' in request.GET and int(request.GET['t']) > 0:
                tipo = int(request.GET['t'])

            if 'tipo' in request.GET and int(request.GET['tipo']) > 0:
                tipodestino = int(request.GET['tipo'])

            if 's' in request.GET:
                search = request.GET['s']

            productos = Producto.objects.filter(activo=True).select_related('unidadmedida', 'tipoproducto')
            if search:
                productos = productos.filter(Q(codigo__icontains=search) | Q(descripcion__icontains=search))

            if tipo and tipodestino:
                productos = productos.filter(tipoproducto__id=tipo, tipo=tipodestino)

            if tipo:
                productos = productos.filter(tipoproducto__id=tipo)

            if tipodestino:
                productos = productos.filter(tipo=tipodestino)

            paging = MiPaginador(productos, 30)
            p = 1
            try:
                if 'page' in request.GET:
                    p = int(request.GET['page'])
                page = paging.page(p)
            except:
                page = paging.page(p)

            data['paging'] = paging
            data['rangospaging'] = paging.rangos_paginado(p)
            data['page'] = page
            data['search'] = search if search else ""
            data['productos'] = page.object_list
            data['categoriaid'] = int(tipo) if tipo else ""
            data['tipoid'] = int(tipodestino) if tipodestino else ""
            data['tipos_productos'] = TipoProducto.objects.all()
            return render_to_response("productos/productos.html", data)
