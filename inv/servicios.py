from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from inv.forms import ServicioForm, RecetaForm
from inv.funciones import (salva_auditoria, MiPaginador, url_back, mensaje_excepcion, ok_json, bad_json)
from inv.models import Servicio, TipoServicio, HistorialPrecioServicio, Receta
from inv.views import addUserData
from spa.settings import ACCION_ADICIONAR, ACCION_MODIFICAR, ACCION_ELIMINAR


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': u'Servicios'}
    addUserData(request, data)
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            f = ServicioForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        servicio = Servicio(codigo=f.cleaned_data['codigo'],
                                            descripcion=f.cleaned_data['descripcion'],
                                            unidadmedida=f.cleaned_data['unidadmedida'],
                                            tiposervicio=f.cleaned_data['tiposervicio'],
                                            alias=f.cleaned_data['alias'],
                                            con_iva=f.cleaned_data['con_iva'],
                                            costo_estandar=f.cleaned_data['costo_estandar'],
                                            precio=f.cleaned_data['precio'],
                                            precio_cliente_normal=f.cleaned_data['precio_cliente_normal'],
                                            precio_cliente_corporativo=f.cleaned_data['precio_cliente_corporativo'],
                                            precio_cliente_vip=f.cleaned_data['precio_cliente_vip'])
                        servicio.save()

                        # Guardar Historial de cambios de precios
                        historialprecio = HistorialPrecioServicio(servicio=servicio,
                                                                  precio=servicio.precio,
                                                                  precio_cliente_normal=servicio.precio_cliente_normal,
                                                                  precio_cliente_corporativo=servicio.precio_cliente_corporativo,
                                                                  precio_cliente_vip=servicio.precio_cliente_vip,
                                                                  usuario=request.user,
                                                                  modulo='S',   # C - Compra, S - Servicios
                                                                  accion=ACCION_ADICIONAR)
                        historialprecio.save()

                        salva_auditoria(request, servicio, ACCION_ADICIONAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'edit':
            servicio = Servicio.objects.get(pk=request.POST['id'])
            f = ServicioForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        flag1 = servicio.precio != f.cleaned_data['precio']
                        flag2 = servicio.precio_cliente_normal != f.cleaned_data['precio_cliente_normal']
                        flag3 = servicio.precio_cliente_corporativo != f.cleaned_data['precio_cliente_corporativo']
                        flag4 = servicio.precio_cliente_vip != f.cleaned_data['precio_cliente_vip']
                        servicio.codigo = f.cleaned_data['codigo']
                        servicio.descripcion = f.cleaned_data['descripcion']
                        servicio.tiposervicio = f.cleaned_data['tiposervicio']
                        servicio.unidadmedida = f.cleaned_data['unidadmedida']
                        servicio.alias = f.cleaned_data['alias']
                        servicio.con_iva = f.cleaned_data['con_iva']
                        servicio.costo_estandar = f.cleaned_data['costo_estandar']
                        servicio.precio = f.cleaned_data['precio']
                        servicio.precio_cliente_normal = f.cleaned_data['precio_cliente_normal']
                        servicio.precio_cliente_corporativo = f.cleaned_data['precio_cliente_corporativo']
                        servicio.precio_cliente_vip = f.cleaned_data['precio_cliente_vip']
                        servicio.save()

                        # Guardar Historial si hubo cambios de precios
                        if flag1 or flag2 or flag3 or flag4:
                            historialprecio = HistorialPrecioServicio(servicio=servicio,
                                                                      precio=servicio.precio,
                                                                      precio_cliente_normal=servicio.precio_cliente_normal,
                                                                      precio_cliente_corporativo=servicio.precio_cliente_corporativo,
                                                                      precio_cliente_vip=servicio.precio_cliente_vip,
                                                                      fecha=datetime.now().date(),
                                                                      usuario=request.user,
                                                                      modulo='S',
                                                                      accion=ACCION_MODIFICAR)
                            historialprecio.save()

                        for ps in servicio.paqueteservicio_set.all():
                            ps.paquete.save()

                        salva_auditoria(request, servicio, ACCION_MODIFICAR)
                    return ok_json()

                except Exception:
                    return bad_json(error=2)
            else:
                return bad_json(error=2)

        elif action == 'delete':
            servicio = Servicio.objects.get(pk=request.POST['id'])
            try:
                with transaction.atomic():
                    salva_auditoria(request, servicio, ACCION_ELIMINAR)
                    servicio.delete()
                return ok_json()

            except Exception:
                return bad_json(error=3)

        elif action == 'get_next_codigo':
            categoria = TipoServicio.objects.get(pk=request.POST['cid'])
            try:
                with transaction.atomic():
                    codigo = "SV-{}-0001".format(categoria.codigo)
                    ultimo_servicio = categoria.get_ultimo_servicio()
                    if ultimo_servicio:
                        codigo = "SV-{}-{}".format(categoria.codigo, str(ultimo_servicio.secuencia_codigo() + 1).zfill(4))
                    return ok_json(data={"codigo": codigo})

            except Exception:
                return bad_json(error=1)

        elif action == 'favorito':
            try:
                servicio = Servicio.objects.get(pk=request.POST['idprod'])
                try:
                    with transaction.atomic():
                        servicio.favorito = False if servicio.favorito else True
                        servicio.save()
                        return ok_json()
                except Exception:
                    return bad_json(error=1)
            except:
                return bad_json(error=1)

        if action == 'addreceta':
            servicio = Servicio.objects.get(pk=request.POST['id'])
            f = RecetaForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        receta = Receta(servicio=servicio,
                                        producto=f.cleaned_data['producto'])
                        receta.save()

                        salva_auditoria(request, receta, ACCION_ADICIONAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'deletereceta':
            receta = Receta.objects.get(pk=request.POST['id'])
            try:
                with transaction.atomic():
                    salva_auditoria(request, receta, ACCION_ELIMINAR)
                    receta.delete()
                return ok_json()

            except Exception:
                return bad_json(error=1)

        return bad_json(error=0)

    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    data['title'] = u'Crear Servicio'
                    data['form'] = ServicioForm()
                    return render_to_response('servicios/add.html', data)
                except Exception as ex:
                    pass

            elif action == 'edit':
                try:
                    data['title'] = u'Modificar Servicio'
                    data['servicio'] = servicio = Servicio.objects.get(pk=request.GET['id'])
                    form = ServicioForm(initial=model_to_dict(servicio))
                    form.for_edit()
                    data['form'] = form
                    return render_to_response('servicios/edit.html', data)
                except Exception as ex:
                    pass

            elif action == 'delete':
                try:
                    data['title'] = u'Eliminar Producto'
                    data['servicio'] = Servicio.objects.get(pk=request.GET['id'])
                    return render_to_response('servicios/delete.html', data)
                except Exception as ex:
                    pass

            elif action == 'receta':
                try:
                    data['title'] = u'Receta del Servicio'
                    data['servicio'] = servicio = Servicio.objects.get(pk=request.GET['id'])
                    data['receta'] = servicio.mi_receta()
                    return render_to_response('servicios/receta.html', data)
                except Exception as ex:
                    pass

            if action == 'addreceta':
                try:
                    data['title'] = u'Adicionar producto a la receta del servicio'
                    data['servicio'] = servicio = Servicio.objects.get(pk=request.GET['id'])
                    form = RecetaForm()
                    form.for_receta(servicio)
                    data['form'] = form
                    return render_to_response('servicios/addreceta.html', data)
                except Exception as ex:
                    pass

            elif action == 'deletereceta':
                try:
                    data['title'] = u'Eliminar producto de la receta'
                    data['receta'] = Receta.objects.get(pk=request.GET['id'])
                    return render_to_response('servicios/deletereceta.html', data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:
            search = None
            tipo = None

            if 't' in request.GET and int(request.GET['t']) > 0:
                tipo = int(request.GET['t'])

            if 's' in request.GET:
                search = request.GET['s']

            servicios = Servicio.objects.filter(activo=True).select_related('unidadmedida', 'tiposervicio')
            if search:
                servicios = servicios.filter(Q(codigo__icontains=search) | Q(descripcion__icontains=search))

            if tipo:
                servicios = servicios.filter(tiposervicio__id=tipo)

            paging = MiPaginador(servicios, 30)
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
            data['servicios'] = page.object_list
            data['categoriaid'] = int(tipo) if tipo else ""
            data['tipos_servicios'] = TipoServicio.objects.all()
            return render_to_response("servicios/servicios.html", data)
