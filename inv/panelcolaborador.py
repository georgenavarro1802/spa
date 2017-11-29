from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from inv.forms import MisSesionesForm
from inv.funciones import url_back, mensaje_excepcion, bad_json, salva_auditoria, ok_json
from inv.models import Sesion, Colaborador
from inv.views import addUserData, ACCION_ADICIONAR
from spa.settings import ACCION_MODIFICAR, ACCION_ELIMINAR


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': u'Panel del Colaborador'}
    addUserData(request, data)
    es_colaborador = data['es_colaborador']
    if not es_colaborador:
        return HttpResponseRedirect('/?info=Ud no es colaborador.')

    colaborador = Colaborador.objects.filter(usuario=request.user)[0]
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'addsesion':
            f = MisSesionesForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        sesion = Sesion(cliente=f.cleaned_data['cliente'],
                                        paquete=f.cleaned_data['paquete'],
                                        colaborador=colaborador,
                                        fecha=f.cleaned_data['fecha'],
                                        proxima_cita=f.cleaned_data['proxima_cita'],
                                        observaciones=f.cleaned_data['observaciones'],
                                        cerrada=f.cleaned_data['cerrada'])
                        sesion.save()
                        salva_auditoria(request, sesion, ACCION_ADICIONAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'editsesion':
            sesion = Sesion.objects.get(pk=request.POST['id'])
            f = MisSesionesForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        sesion.paquete = f.cleaned_data['paquete']
                        sesion.cliente = f.cleaned_data['cliente']
                        sesion.fecha = f.cleaned_data['fecha']
                        sesion.proxima_cita = f.cleaned_data['proxima_cita']
                        sesion.observaciones = f.cleaned_data['observaciones']
                        sesion.cerrada = f.cleaned_data['cerrada']
                        sesion.save()
                        salva_auditoria(request, sesion, ACCION_MODIFICAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=2)
            else:
                return bad_json(error=2)

        elif action == 'deletesesion':
            try:
                sesion = Sesion.objects.get(pk=request.POST['id'])
                with transaction.atomic():
                    salva_auditoria(request, sesion, ACCION_ELIMINAR)
                    sesion.delete()
                    return ok_json()
            except Exception:
                return bad_json(error=3)

        return bad_json(error=0)

    else:

        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'missesiones':
                try:
                    data['mis_sesiones'] = colaborador.sesion_set.all()
                    return render_to_response("panelcolaborador/missesiones.html", data)
                except Exception:
                    pass

            elif action == 'addsesion':
                try:
                    data['title'] = u'Crear Sesión'
                    data['form'] = MisSesionesForm(initial={'fecha': datetime.now().date()})
                    return render_to_response("panelcolaborador/add.html", data)
                except Exception as ex:
                    pass

            elif action == 'editsesion':
                try:
                    data['title'] = u'Editar Sesión'
                    data['sesion'] = sesion = Sesion.objects.get(pk=request.GET['id'])
                    data['form'] = MisSesionesForm(initial={'paquete': sesion.paquete,
                                                            'cliente': sesion.cliente,
                                                            'colaborador': sesion.colaborador,
                                                            'fecha': sesion.fecha,
                                                            'observaciones': sesion.observaciones,
                                                            'proxima_cita': sesion.proxima_cita})
                    return render_to_response("panelcolaborador/edit.html", data)
                except Exception as ex:
                    pass

            elif action == 'deletesesion':
                try:
                    data['title'] = u'Borrar Sesión'
                    data['sesion'] = Sesion.objects.get(pk=request.GET['id'])
                    return render_to_response("panelcolaborador/delete.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:
            return render_to_response("panelcolaborador/view.html", data)
