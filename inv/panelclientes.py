from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from inv.forms import ValoracionForm
from inv.funciones import mensaje_excepcion, url_back, salva_auditoria, ok_json, bad_json
from inv.models import Cliente, DetalleFactura
from inv.views import addUserData
from spa.settings import ACCION_MODIFICAR


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': u'Panel del Cliente'}
    addUserData(request, data)
    if Cliente.objects.filter(usuario=request.user).exists():
        data['cliente'] = cliente = Cliente.objects.filter(usuario=request.user)[0]
    else:
        return HttpResponseRedirect("/salir")

    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST['action']

            if action == 'valorar_servicio':
                detalle_factura = DetalleFactura.objects.get(pk=int(request.POST['id']))
                f = ValoracionForm(request.POST)
                if f.is_valid():
                    try:
                        with transaction.atomic():
                            detalle_factura.valoracion_servicio = f.cleaned_data['valoracion']
                            detalle_factura.recomendaciones_servicio = f.cleaned_data['recomendaciones']
                            detalle_factura.save()
                            salva_auditoria(request, detalle_factura, ACCION_MODIFICAR)
                            return ok_json()

                    except Exception:
                        return bad_json(error=1)
                else:
                    return bad_json(error=1)

            elif action == 'valorar_producto':
                detalle_factura = DetalleFactura.objects.get(pk=int(request.POST['id']))
                f = ValoracionForm(request.POST)
                if f.is_valid():
                    try:
                        with transaction.atomic():
                            detalle_factura.valoracion_producto = f.cleaned_data['valoracion']
                            detalle_factura.recomendaciones_producto = f.cleaned_data['recomendaciones']
                            detalle_factura.save()
                            salva_auditoria(request, detalle_factura, ACCION_MODIFICAR)
                            return ok_json()

                    except Exception:
                        return bad_json(error=1)
                else:
                    return bad_json(error=1)

        return bad_json(error=0)

    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'cliente_servicios_recibidos':
                try:
                    data['detalles_facturas'] = DetalleFactura.objects.filter(servicio__isnull=False,
                                                                              factura__cliente=cliente).distinct().order_by('factura')
                    return render_to_response("panelclientes/cliente_servicios_recibidos.html", data)
                except Exception as ex:
                    pass

            elif action == 'valorar_servicio':
                try:
                    data['detalle_factura'] = df = DetalleFactura.objects.get(pk=int(request.GET['id']))
                    data['form'] = ValoracionForm(initial={'valoracion': df.valoracion_servicio,
                                                           'recomendaciones': df.recomendaciones_servicio})
                    return render_to_response("panelclientes/valorar_servicio.html", data)
                except Exception as ex:
                    pass

            elif action == 'cliente_productos_comprados':
                try:
                    data['detalles_facturas'] = DetalleFactura.objects.filter(producto__isnull=False, factura__cliente=cliente).distinct().order_by('factura')
                    return render_to_response("panelclientes/cliente_productos_comprados.html", data)
                except Exception as ex:
                    pass

            elif action == 'valorar_producto':
                try:
                    data['detalle_factura'] = df = DetalleFactura.objects.get(pk=int(request.GET['id']))
                    data['form'] = ValoracionForm(initial={'valoracion': df.valoracion_producto,
                                                           'recomendaciones': df.recomendaciones_producto})
                    return render_to_response("panelclientes/valorar_producto.html", data)
                except Exception as ex:
                    pass

            elif action == 'cliente_servicios_futuros':
                try:
                    data['servicios_futuros'] = cliente.mis_servicios_futuros()
                    return render_to_response("panelclientes/cliente_servicios_futuros.html", data)
                except Exception as ex:
                    pass

            elif action == 'cliente_paquetes':
                try:
                    data['paquetes'] = ""
                    return render_to_response("panelclientes/cliente_paquetes.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:
            return render_to_response("panelclientes/view.html", data)
