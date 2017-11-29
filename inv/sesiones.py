from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from inv.forms import SesionesForm
from inv.funciones import salva_auditoria, MiPaginador, mensaje_excepcion, url_back, bad_json, ok_json
from inv.models import Sesion, Factura
from inv.views import addUserData
from spa.settings import (ACCION_ADICIONAR, ACCION_MODIFICAR, ACCION_ELIMINAR)


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': u'Control de Sesiones de Paquetes'}
    addUserData(request, data)
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            f = SesionesForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        sesion = Sesion(factura=f.cleaned_data['factura'],
                                        cliente=f.cleaned_data['cliente'],
                                        paquete=f.cleaned_data['paquete'],
                                        colaborador=f.cleaned_data['colaborador'],
                                        fecha=f.cleaned_data['fecha'],
                                        proxima_cita=f.cleaned_data['proxima_cita'],
                                        observaciones=f.cleaned_data['observaciones'],
                                        cerrada=False)
                        sesion.save()
                        salva_auditoria(request, sesion, ACCION_ADICIONAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'edit':
            sesion = Sesion.objects.get(pk=request.POST['id'])
            f = SesionesForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        sesion.factura = f.cleaned_data['factura']
                        sesion.paquete = f.cleaned_data['paquete']
                        sesion.cliente = f.cleaned_data['cliente']
                        sesion.colaborador = f.cleaned_data['colaborador']
                        sesion.fecha = f.cleaned_data['fecha']
                        sesion.proxima_cita = f.cleaned_data['proxima_cita']
                        sesion.observaciones = f.cleaned_data['observaciones']
                        sesion.save()
                        salva_auditoria(request, sesion, ACCION_MODIFICAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=2)
            else:
                return bad_json(error=2)

        elif action == 'delete':
            try:
                sesion = Sesion.objects.get(pk=request.POST['id'])
                with transaction.atomic():
                    salva_auditoria(request, sesion, ACCION_ELIMINAR)
                    sesion.delete()
                    return ok_json()

            except Exception:
                return bad_json(error=3)

        elif action == 'get_factura_data':
            try:
                factura = Factura.objects.get(pk=request.POST['idfact'])
                cliente = factura.cliente
                colaborador = factura.mis_colaboradores()[0] if factura.mis_colaboradores() else None
                paquete = factura.detallefactura_set.filter(paquete__isnull=False)[0].paquete
                return ok_json(data={'cliente': cliente.id if cliente else "",
                                     'paquete': paquete.id if paquete else "",
                                     'fecha': factura.fecha.strftime('%d-%m-%Y'),
                                     'colaborador': colaborador.id if colaborador else ""})
            except Exception:
                return bad_json(error=1)

        return bad_json(error=0)

    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    data['title'] = u'Crear Sesión'
                    form = SesionesForm(initial={'fecha': datetime.now().date()})
                    form.solo_facturas_con_paquetes()
                    data['form'] = form
                    return render_to_response("sesiones/add.html", data)
                except Exception as ex:
                    pass

            elif action == 'edit':
                try:
                    data['title'] = u'Editar Sesión'
                    data['sesion'] = sesion = Sesion.objects.get(pk=request.GET['id'])
                    form = SesionesForm(initial={'factura': sesion.factura,
                                                 'paquete': sesion.paquete,
                                                 'cliente': sesion.cliente,
                                                 'colaborador': sesion.colaborador,
                                                 'fecha': sesion.fecha,
                                                 'observaciones': sesion.observaciones,
                                                 'proxima_cita': sesion.proxima_cita})
                    form.solo_facturas_con_paquetes()
                    data['form'] = form
                    return render_to_response("sesiones/edit.html", data)
                except Exception as ex:
                    pass

            elif action == 'delete':
                try:
                    data['title'] = u'Borrar Sesión'
                    data['sesion'] = Sesion.objects.get(pk=request.GET['id'])
                    return render_to_response("sesiones/delete.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:
            search = None

            if 's' in request.GET:
                search = request.GET['s']

            sesiones = Sesion.objects.all().select_related('paquete', 'cliente', 'colaborador')
            if search:
                sesiones = sesiones.filter(Q(cliente__nombre__icontains=search) |
                                           Q(cliente__ruc__icontains=search) |
                                           Q(cliente__identificacion__icontains=search))

            paging = MiPaginador(sesiones, 30)
            p = 1
            try:
                if 'page' in request.GET:
                    p = int(request.GET['page'])
                page = paging.page(p)
            except:
                page = paging.page(1)
            data['paging'] = paging
            data['rangospaging'] = paging.rangos_paginado(p)
            data['page'] = page
            data['search'] = search if search else ""
            data['sesiones'] = page.object_list
            return render_to_response("sesiones/view.html", data)
