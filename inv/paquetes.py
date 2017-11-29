from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from inv.forms import PaqueteForm, PaqueteProductoForm, PaqueteServicioForm
from inv.funciones import (salva_auditoria, url_back, mensaje_excepcion, bad_json, ok_json)
from inv.models import Servicio, TipoServicio, Paquete, PaqueteProducto, PaqueteServicio
from inv.views import addUserData
from spa.settings import ACCION_ADICIONAR, ACCION_MODIFICAR, ACCION_ELIMINAR, PAQUETE_PROMOCIONAL, PAQUETE_MULTISESION


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': 'Paquetes'}
    addUserData(request, data)
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            f = PaqueteForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        codigo = f.cleaned_data['codigo']
                        tipo = int(f.cleaned_data['tipo'])
                        sesiones = int(f.cleaned_data['sesiones'])
                        if Paquete.objects.filter(codigo=codigo).exists():
                            return bad_json(mensaje=u"Ya existe un paquete con ese código.")
                        if (tipo == PAQUETE_PROMOCIONAL or tipo == PAQUETE_MULTISESION) and sesiones < 2:
                            return bad_json(mensaje=u"La cantidad de sesión no puede ser menor a 2 "
                                                    u"por el tipo de paquete seleccionado")
                        paquete = Paquete(codigo=codigo,
                                          descripcion=f.cleaned_data['descripcion'],
                                          alias=f.cleaned_data['alias'],
                                          tipo=tipo,
                                          sesiones=sesiones)
                        paquete.save()
                        salva_auditoria(request, paquete, ACCION_ADICIONAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'edit':
            paquete = Paquete.objects.get(pk=request.POST['id'])
            f = PaqueteForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        codigo = f.cleaned_data['codigo']
                        tipo = int(f.cleaned_data['tipo'])
                        sesiones = int(f.cleaned_data['sesiones'])
                        if Paquete.objects.filter(codigo=codigo).exclude(id=paquete.id).exists():
                            return bad_json(mensaje=u"Ya existe un paquete con ese código.")
                        if (tipo == PAQUETE_PROMOCIONAL or tipo == PAQUETE_MULTISESION) and sesiones < 2:
                            return bad_json(mensaje=u"La cantidad de sesión no puede ser menor a 2 "
                                                    u"por el tipo de paquete seleccionado")
                        paquete.codigo = f.cleaned_data['codigo']
                        paquete.descripcion = f.cleaned_data['descripcion']
                        paquete.alias = f.cleaned_data['alias']
                        paquete.tipo = tipo
                        paquete.sesiones = sesiones
                        paquete.save()
                        salva_auditoria(request, paquete, ACCION_MODIFICAR)
                    return ok_json()

                except Exception:
                    return bad_json(error=2)
            else:
                return bad_json(error=2)

        elif action == 'delete':
            paquete = Paquete.objects.get(pk=request.POST['id'])
            try:
                with transaction.atomic():
                    salva_auditoria(request, paquete, ACCION_ELIMINAR)
                    paquete.delete()
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

        if action == 'addelementoproducto':
            paquete = Paquete.objects.get(pk=request.POST['id'])
            f = PaqueteProductoForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        pp = PaqueteProducto(paquete=paquete,
                                             producto=f.cleaned_data['producto'])
                        pp.save()
                        pp.paquete.save()   # actualizar precios
                        salva_auditoria(request, pp, ACCION_ADICIONAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        if action == 'addelementoservicio':
            paquete = Paquete.objects.get(pk=request.POST['id'])
            f = PaqueteServicioForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        ps = PaqueteServicio(paquete=paquete,
                                             servicio=f.cleaned_data['servicio'])
                        ps.save()
                        ps.paquete.save()   # actualizar precios
                        salva_auditoria(request, ps, ACCION_ADICIONAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'deleteelementoproducto':
            pp = PaqueteProducto.objects.get(pk=request.POST['id'])
            paquete = pp.paquete
            try:
                with transaction.atomic():
                    salva_auditoria(request, pp, ACCION_ELIMINAR)
                    pp.delete()
                    paquete.save()
                return ok_json()

            except Exception:
                return bad_json(error=1)

        elif action == 'deleteelementoservicio':
            ps = PaqueteServicio.objects.get(pk=request.POST['id'])
            paquete = ps.paquete
            try:
                with transaction.atomic():
                    salva_auditoria(request, ps, ACCION_ELIMINAR)
                    ps.delete()
                    paquete.save()
                return ok_json()

            except Exception:
                return bad_json(error=1)

        elif action == 'valor_precios_clientes':
            paquete = Paquete.objects.get(pk=request.POST['pid'])
            try:
                porciento_cliente_normal = float(request.POST['porciento_cliente_normal'])
                porciento_cliente_corporativo = float(request.POST['porciento_cliente_corporativo'])
                porciento_cliente_vip = float(request.POST['porciento_cliente_vip'])

                paquete.porciento_cliente_normal = porciento_cliente_normal
                paquete.porciento_cliente_corporativo = porciento_cliente_corporativo
                paquete.porciento_cliente_vip = porciento_cliente_vip
                paquete.save()

                return ok_json(data={"valor_cliente_normal": paquete.valor_cliente_normal,
                                     "valor_cliente_corporativo": paquete.valor_cliente_corporativo,
                                     "valor_cliente_vip": paquete.valor_cliente_vip})
            except Exception:
                return bad_json(error=1)

        return bad_json(error=0)

    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    data['title'] = u'Crear Paquete'
                    data['form'] = PaqueteForm()
                    return render_to_response('paquetes/add.html', data)
                except Exception as ex:
                    pass

            elif action == 'edit':
                try:
                    data['title'] = u'Modificar Paquete'
                    data['paquete'] = paquete = Paquete.objects.get(pk=request.GET['id'])
                    data['form'] = PaqueteForm(initial=model_to_dict(paquete))
                    return render_to_response('paquetes/edit.html', data)
                except Exception as ex:
                    pass

            elif action == 'delete':
                try:
                    data['title'] = u'Eliminar Paquete'
                    data['paquete'] = Paquete.objects.get(pk=request.GET['id'])
                    return render_to_response('paquetes/delete.html', data)
                except Exception as ex:
                    pass

            elif action == 'elementos':
                try:
                    data['title'] = u'Elementos del Paquete'
                    data['paquete'] = Paquete.objects.get(pk=request.GET['id'])
                    return render_to_response('paquetes/elementos.html', data)
                except Exception as ex:
                    pass

            if action == 'addelementoproducto':
                try:
                    data['title'] = u'Adicionar producto al paquete'
                    data['paquete'] = paquete = Paquete.objects.get(pk=request.GET['id'])
                    form = PaqueteProductoForm()
                    form.for_paquete(paquete)
                    data['form'] = form
                    return render_to_response('paquetes/addelementoproducto.html', data)
                except Exception as ex:
                    pass

            if action == 'addelementoservicio':
                try:
                    data['title'] = u'Adicionar servicio al paquete'
                    data['paquete'] = paquete = Paquete.objects.get(pk=request.GET['id'])
                    form = PaqueteServicioForm()
                    form.for_paquete(paquete)
                    data['form'] = form
                    return render_to_response('paquetes/addelementoservicio.html', data)
                except Exception as ex:
                    pass

            elif action == 'deleteelementoproducto':
                try:
                    data['title'] = u'Eliminar producto del paquete'
                    data['paqueteproducto'] = pp = PaqueteProducto.objects.get(pk=request.GET['id'])
                    data['paquete'] = pp.paquete
                    return render_to_response('paquetes/deleteelementoproducto.html', data)
                except Exception as ex:
                    pass

            elif action == 'deleteelementoservicio':
                try:
                    data['title'] = u'Eliminar servicio del paquete'
                    data['paqueteservicio'] = ps = PaqueteServicio.objects.get(pk=request.GET['id'])
                    data['paquete'] = ps.paquete
                    return render_to_response('paquetes/deleteelementoservicio.html', data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:
            search = None

            if 's' in request.GET:
                search = request.GET['s']

            paquetes = Paquete.objects.filter(activo=True)
            if search:
                paquetes = paquetes.filter(Q(codigo__icontains=search) | Q(descripcion__icontains=search))

            data['search'] = search if search else ""
            data['paquetes'] = paquetes
            return render_to_response("paquetes/paquetes.html", data)
