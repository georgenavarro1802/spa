from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from inv.forms import SesionCajaForm, CierreSesionCajaForm
from inv.funciones import salva_auditoria, MiPaginador, url_back, mensaje_excepcion, ok_json, bad_json
from inv.models import SesionCaja
from inv.views import addUserData
from spa.settings import ACCION_MODIFICAR


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': u'Sesiones de Caja'}
    addUserData(request, data)

    usuario = request.user
    if not data['es_cajero']:
        return HttpResponseRedirect("/?info=El usuario no tiene permisos como cajero")
    data['cajero'] = cajero = usuario.cajero_set.all()[0]

    if request.method == 'POST':
        action = request.POST['action']

        if action == 'abrirsesion':
            f = SesionCajaForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        sc = SesionCaja(cajero=cajero,
                                        fecha=datetime.now(),
                                        fondo=f.cleaned_data['fondo'],
                                        abierta=True)
                        sc.save()
                        salva_auditoria(request, sc, ACCION_MODIFICAR, 'Abierta sesion de caja: ' + sc.__str__())
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'closesesion':
            sc = SesionCaja.objects.get(pk=request.POST['id'])
            f = CierreSesionCajaForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        sc.bill100 = f.cleaned_data['bill100']
                        sc.bill50 = f.cleaned_data['bill50']
                        sc.bill20 = f.cleaned_data['bill20']
                        sc.bill10 = f.cleaned_data['bill10']
                        sc.bill5 = f.cleaned_data['bill5']
                        sc.bill2 = f.cleaned_data['bill2']
                        sc.bill1 = f.cleaned_data['bill1']
                        sc.enmonedas = f.cleaned_data['enmonedas']
                        sc.cheque = f.cleaned_data['cheque']
                        sc.deposito = f.cleaned_data['deposito']
                        sc.transferencia = f.cleaned_data['transferencia']
                        sc.abierta = False
                        sc.fechacierre = datetime.now()
                        sc.horacierre = datetime.now().time()
                        sc.save()
                        salva_auditoria(request, sc, ACCION_MODIFICAR, 'Cerrada sesion de caja: {}'.format(sc))
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        return bad_json(error=0)

    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'addsesion':
                try:
                    data['title'] = u'Abrir Sesión de Caja'
                    data['form'] = SesionCajaForm(initial={'fondo': '0.00'})
                    return render_to_response("caja/adicionarbs.html", data)
                except Exception as ex:
                    pass

            elif action == 'closesesion':
                try:
                    data['title'] = u'Cierre Sesión de Caja'
                    data['sesion'] = SesionCaja.objects.get(pk=request.GET['id'])
                    data['form'] = CierreSesionCajaForm(initial={'bill100': 0,
                                                                 'bill50': 0,
                                                                 'bill20': 0,
                                                                 'bill10': 0,
                                                                 'bill5': 0,
                                                                 'bill2': 0,
                                                                 'bill1': 0,
                                                                 'enmonedas': 0.00,
                                                                 'cheque': 0.00,
                                                                 'deposito': 0.00,
                                                                 'transferencia': 0.00,
                                                                 'total': 0.00})
                    return render_to_response("caja/cerrarsesionbs.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:
            sesiones = cajero.sesiones_caja()
            paging = MiPaginador(sesiones, 30)
            p = 1
            try:
                if 'page' in request.GET:
                    p = int(request.GET['page'])
                sesionespagina = paging.page(p)
            except:
                sesionespagina = paging.page(1)
            data['paging'] = paging
            data['rangospaging'] = paging.rangos_paginado(p)
            data['page'] = sesionespagina
            data['sesiones'] = sesionespagina.object_list
            return render_to_response("caja/sesionesbs.html", data)
