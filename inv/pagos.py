import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import render_to_response

from inv.forms import PagoForm, TransaccionPagoForm
from inv.funciones import model_to_dict_safe, ok_json, bad_json
from inv.models import *
from inv.views import addUserData, convertir_fecha
from spa.settings import (FORMA_PAGO_EFECTIVO, FORMA_PAGO_CHEQUE, FORMA_PAGO_DEPOSITO, FORMA_PAGO_TARJETA,
                          FORMA_PAGO_TRANSFERENCIA, FORMA_PAGO_RETENCION)


class ErrorPagos(Exception):

    def __init__(self, valor):
        self.valor = valor

    def __str__(self):
        return self.valor


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    data = {'title': u'Cobros'}
    addUserData(request, data)
    data['empresa'] = request.session['empresa']

    if request.method == 'POST':
        action = request.POST['action']

        if action == 'pendientes':
            cliente = Cliente.objects.get(pk=request.POST['cid'])
            ventas = cliente.factura_set.filter(total__gt=F('pagado'), valida=True).order_by('-fecha_vencimiento', 'numero')
            totalpendiente = 0
            totalpagado = 0
            lista = []
            for a in ventas:
                d = model_to_dict_safe(a, exclude=['fecha', 'fecha_vencimiento', 'detalles'])
                d['fecha'] = a.fecha_vencimiento.strftime("%d-%m-%Y")
                d['cantidad_productos'] = a.cantidad_productos()
                totalpendiente += (a.total - a.pagado)
                totalpagado += a.pagado
                lista.append(d)

            return ok_json(data={"datos": lista, "totalpendiente": totalpendiente, "totalpagado": totalpagado})

        elif action == 'pago':
            datos = json.loads(request.POST['datos'])
            total = 0
            try:
                with transaction.atomic():
                    # Facturas seleccionadas
                    for documento in datos['ingresosapagar']:
                        factura = Factura.objects.get(pk=documento['id'])
                        # Pagos asociados
                        for p in datos['pagos']:
                            if p['formapago'] == str(FORMA_PAGO_EFECTIVO):
                                pago = Pago(factura=factura,
                                            fecha=convertir_fecha(p['fechaefectivo']),
                                            valor=float(p['valor']),
                                            observaciones=p['observaciones'])
                                pago.save()
                                pagoefectivo = PagoEfectivo(pago=pago)
                                pagoefectivo.save()
                                total += pagoefectivo.pago.valor

                            elif p['formapago'] == str(FORMA_PAGO_CHEQUE):
                                pago = Pago(factura=factura,
                                            fecha=convertir_fecha(p['fechacheque']),
                                            valor=float(p['valor']),
                                            observaciones=p['observaciones'])
                                pago.save()
                                pagocheque = PagoCheque(pago=pago,
                                                        numero=p['numerocheque'],
                                                        banco_id=p['bancocheque'],
                                                        postfechado=True if int(p['postfechado']) == 1 else False,
                                                        depositado=True if int(p['depositado']) == 1 else False,
                                                        fechadepositado=convertir_fecha(p['fechadepositado']),
                                                        emite=p['emite'])
                                pagocheque.save()
                                total += pagocheque.pago.valor

                            elif p['formapago'] == str(FORMA_PAGO_DEPOSITO):
                                pago = Pago(factura=factura,
                                            fecha=convertir_fecha(p['fechadeposito']),
                                            valor=float(p['valor']),
                                            observaciones=p['observaciones'])
                                pago.save()
                                pagodeposito = PagoDeposito(pago=pago,
                                                            numero=p['numerodeposito'],
                                                            efectuadopor=p['efectuadopor'])
                                pagodeposito.save()
                                total += pagodeposito.pago.valor

                            elif p['formapago'] == str(FORMA_PAGO_TRANSFERENCIA):
                                pago = Pago(factura=factura,
                                            fecha=convertir_fecha(p['fechatransferencia']),
                                            valor=float(p['valor']),
                                            observaciones=p['observaciones'])
                                pago.save()
                                pagotransferencia = PagoTransferencia(pago=pago,
                                                                      numero=p['numerotransferencia'],
                                                                      efectuadopor=p['efectuadopor'])
                                pagotransferencia.save()
                                total += pagotransferencia.pago.valor

                            elif p['formapago'] == str(FORMA_PAGO_TARJETA):
                                if PagoTarjeta.objects.filter(referencia=p['referencia'], lote=p['lote']).exists():
                                    return bad_json(extradata={'result': 'repeat'})
                                pago = Pago(factura=factura,
                                            fecha=convertir_fecha(p['fechatarjeta']),
                                            valor=float(p['valor']),
                                            observaciones=p['observaciones'])
                                pago.save()
                                pagotarjeta = PagoTarjeta(pago=pago,
                                                          banco_id=p['bancotarjeta'],
                                                          tipotarjeta_id=p['tipotarjeta'],
                                                          poseedor=p['poseedor'],
                                                          procesadorpago_id=p['procesadorpago'],
                                                          referencia=p['referencia'],
                                                          lote=p['lote'])
                                pagotarjeta.save()
                                total += pagotarjeta.pago.valor

                            elif p['formapago'] == str(FORMA_PAGO_RETENCION):
                                pago = Pago(factura=factura,
                                            fecha=convertir_fecha(p['fecharetencion']),
                                            valor=float(p['valor']),
                                            observaciones=p['observaciones'])
                                pago.save()
                                pagoretencion = PagoRetencion(pago=pago,
                                                              numero=p['numeroretencion'])
                                pagoretencion.save()
                                total += pagoretencion.pago.valor

                        factura.pagado += total
                        factura.save()

                    return ok_json()

            except Exception:
                return bad_json(error=1)

        return bad_json(error=0)

    else:
        try:
            cliente = None
            if 'cid' in request.GET and int(request.GET['cid']) > 0 and Cliente.objects.filter(pk=int(request.GET['cid'])).exists():
                cliente = Cliente.objects.filter(pk=int(request.GET['cid']))[0]

            data['hoy'] = hoy = datetime.now().date()
            data['form'] = PagoForm()
            data['form3'] = TransaccionPagoForm(initial={'valor': 0,
                                                         'fechacheque': hoy,
                                                         'fechaefectivo': hoy,
                                                         'fechadeposito': hoy,
                                                         'fechatransferencia': hoy,
                                                         'fechatarjeta': hoy,
                                                         'fechadepositado': hoy})
            data['formasdepago'] = FormaDePago.objects.all()
            data['forma_pago_efectivo'] = FORMA_PAGO_EFECTIVO
            data['forma_pago_cheque'] = FORMA_PAGO_CHEQUE
            data['forma_pago_deposito'] = FORMA_PAGO_DEPOSITO
            data['forma_pago_transferencia'] = FORMA_PAGO_TRANSFERENCIA
            data['forma_pago_tarjeta'] = FORMA_PAGO_TARJETA
            data['forma_pago_retencion'] = FORMA_PAGO_RETENCION
            data['procesadorespago'] = ProcesadorPagoTarjeta.objects.all()
            data['tipostarjeta'] = TipoTarjetaBanco.objects.all()
            data['cliente'] = cliente
            return render_to_response("pagos/view.html", data)

        except Exception:
            pass
