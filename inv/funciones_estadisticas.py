from django.db.models import F
from inv.models import *


#  V E N T A S  #################################################

def valores_ventas_total():
    valor = Factura.objects.filter(valida=True).aggregate(suma=Sum('total'))['suma']
    return valor if valor else 0


def valores_ventas_total_fechas(inicio, fin):
    valor = Factura.objects.filter(valida=True, fecha__range=(inicio, fin)).aggregate(suma=Sum('total'))['suma']
    return valor if valor else 0


def valores_ventas_total_mes_anio(mes, anio):
    valor = Factura.objects.filter(valida=True, fecha__month=mes, fecha__year=anio).aggregate(suma=Sum('total'))['suma']
    return valor if valor else 0


def valores_ventas_subtotal_fechas(inicio, fin):
    valor = Factura.objects.filter(valida=True, fecha__range=(inicio, fin)).aggregate(suma=Sum('subtotal'))['suma']
    return valor if valor else 0


def valores_ventas_subtotal_mes_anio(mes, anio):
    valor = Factura.objects.filter(valida=True, fecha__month=mes, fecha__year=anio).aggregate(suma=Sum('subtotal'))['suma']
    return valor if valor else 0


def valores_ventas_iva_fechas(inicio, fin):
    valor = Factura.objects.filter(valida=True, fecha__range=(inicio, fin)).aggregate(suma=Sum('iva'))['suma']
    return valor if valor else 0


def valores_ventas_iva_mes_anio(mes, anio):
    valor = Factura.objects.filter(valida=True, fecha__month=mes, fecha__year=anio).aggregate(suma=Sum('iva'))['suma']
    return valor if valor else 0


def cantidad_facturas_fechas(inicio, fin):
    return Factura.objects.filter(valida=True, fecha__range=(inicio, fin)).count()


def cantidad_facturas_mes_anio(mes, anio):
    return Factura.objects.filter(valida=True, fecha__month=mes, fecha__year=anio).count()


def cantidad_facturas_total():
    return Factura.objects.filter(valida=True).count()


# P A G O S #####################################
def pagos_total():
    valor = Pago.objects.aggregate(suma=Sum('valor'))['suma']
    return valor if valor else 0


def cantidad_pagos_total():
    return Pago.objects.all().count()


def pagos_total_fechas(inicio, fin):
    valor = Pago.objects.filter(fecha__range=(inicio, fin)).aggregate(suma=Sum('valor'))['suma']
    return valor if valor else 0


def pagos_total_mes_anio(mes, anio):
    valor = Pago.objects.filter(fecha__month=mes, fecha__year=anio).aggregate(suma=Sum('valor'))['suma']
    return valor if valor else 0


def pagos_efectivo_fechas(inicio, fin):
    valor = PagoEfectivo.objects.filter(pago__fecha__range=(inicio, fin)).aggregate(suma=Sum('pago__valor'))['suma']
    return valor if valor else 0


def pagos_cheque_fechas(inicio, fin):
    valor = PagoCheque.objects.filter(pago__fecha__range=(inicio, fin),
                                      depositado=True).aggregate(suma=Sum('pago__valor'))['suma']
    return valor if valor else 0


def pagos_deposito_fechas(inicio, fin):
    valor = PagoDeposito.objects.filter(pago__fecha__range=(inicio, fin)).aggregate(suma=Sum('pago__valor'))['suma']
    return valor if valor else 0


def pagos_transferencia_fechas(inicio, fin):
    valor = PagoTransferencia.objects.filter(pago__fecha__range=(inicio, fin)).aggregate(suma=Sum('pago__valor'))['suma']
    return valor if valor else 0


def pagos_tarjeta_fechas(inicio, fin):
    valor = PagoTarjeta.objects.filter(pago__fecha__range=(inicio, fin)).aggregate(suma=Sum('pago__valor'))['suma']
    return valor if valor else 0


def pagos_retencion_fechas(inicio, fin):
    valor = PagoRetencion.objects.filter(pago__fecha__range=(inicio, fin)).aggregate(suma=Sum('pago__valor'))['suma']
    return valor if valor else 0


def pagos_porciento_efectivo_fechas(inicio, fin):
    if pagos_total_fechas(inicio, fin):
        return round(pagos_efectivo_fechas(inicio, fin) / pagos_total_fechas(inicio, fin) * 100, 2)
    return 0


def pagos_porciento_cheque_fechas(inicio, fin):
    if pagos_total_fechas(inicio, fin):
        return round(pagos_cheque_fechas(inicio, fin) / pagos_total_fechas(inicio, fin) * 100, 2)
    return 0


def pagos_porciento_deposito_fechas(inicio, fin):
    if pagos_total_fechas(inicio, fin):
        return round(pagos_deposito_fechas(inicio, fin) / pagos_total_fechas(inicio, fin) * 100, 2)
    return 0


def pagos_porciento_transferencia_fechas(inicio, fin):
    if pagos_total_fechas(inicio, fin):
        return round(pagos_transferencia_fechas(inicio, fin) / pagos_total_fechas(inicio, fin) * 100, 2)
    return 0


def pagos_porciento_tarjeta_fechas(inicio, fin):
    if pagos_total_fechas(inicio, fin):
        return round(pagos_tarjeta_fechas(inicio, fin) / pagos_total_fechas(inicio, fin) * 100, 2)
    return 0


def pagos_porciento_retencion_fechas(inicio, fin):
    if pagos_total_fechas(inicio, fin):
        return round(pagos_retencion_fechas(inicio, fin) / pagos_total_fechas(inicio, fin) * 100, 2)
    return 0


def cantidad_facturas_pagos_efectivo_fechas(inicio, fin):
    return Factura.objects.filter(pago__pagoefectivo__isnull=False, pago__fecha__range=(inicio, fin),
                                  valida=True).distinct().count()


def cantidad_facturas_pagos_cheque_fechas(inicio, fin):
    return Factura.objects.filter(pago__pagocheque__isnull=False, pago__fecha__range=(inicio, fin),
                                  valida=True).distinct().count()


def cantidad_facturas_pagos_deposito_fechas(inicio, fin):
    return Factura.objects.filter(pago__pagodeposito__isnull=False, pago__fecha__range=(inicio, fin),
                                  valida=True).distinct().count()


def cantidad_facturas_pagos_transferencia_fechas(inicio, fin):
    return Factura.objects.filter(pago__pagotransferencia__isnull=False, pago__fecha__range=(inicio, fin),
                                  valida=True).distinct().count()


def cantidad_facturas_pagos_tarjeta_fechas(inicio, fin):
    return Factura.objects.filter(pago__pagotarjeta__isnull=False, pago__fecha__range=(inicio, fin),
                                  valida=True).distinct().count()


def cantidad_facturas_pagos_retencion_fechas(inicio, fin):
    return Factura.objects.filter(pago__pagoretencion__isnull=False, pago__fecha__range=(inicio, fin),
                                  valida=True).distinct().count()


def cantidad_facturas_pagos_total_fechas(inicio, fin):
    return Factura.objects.filter(pago__isnull=False, pago__fecha__range=(inicio, fin), valida=True).distinct().count()


# COMPRAS, INVENTARIOS, OTROS #############
def valor_total_fob_compras():
    valor = IngresoProducto.objects.aggregate(suma=Sum('valorfob'))['suma']
    return round(valor, 2) if valor else 0


def valor_total_cif_compras():
    valor = IngresoProducto.objects.aggregate(suma=Sum('valor'))['suma']
    return round(valor, 2) if valor else 0


def valor_total_productos_comision_ventas():
    valor = 0
    for producto in Producto.objects.all():
        valor += producto.valor_comision_ventas()
    return round(valor, 2) if valor else 0


def valor_total_productos_pagos_retencion():
    valor = 0
    for producto in Producto.objects.all():
        valor += producto.valor_pagos_retencion()
    return round(valor, 2) if valor else 0


def valor_total_productos_ventas():
    valor = 0
    for producto in Producto.objects.all():
        valor += producto.valor_ventas()
    return round(valor, 2) if valor else 0


def ganancia_total():
    return valor_total_productos_ventas() - (
        valor_total_cif_compras() + valor_total_productos_comision_ventas() + valor_total_productos_pagos_retencion())


def cantidad_compras_total():
    return IngresoProducto.objects.count()


def cantidad_inventario_con_existencia():
    return InventarioReal.objects.filter(cantidad__gt=0).count()


def valor_inventario_con_existencia():
    valor = InventarioReal.objects.filter(cantidad__gt=0).aggregate(suma=Sum('valor'))['suma']
    return round(valor, 2) if valor else 0


def cantidad_facturas_por_cancelar():
    return Factura.objects.filter(valida=True, cancelada=False).count()


def valor_facturas_por_cancelar():
    valor = 0
    for f in Factura.objects.filter(valida=True, cancelada=False):
        valor += f.saldo_pendiente()
    return round(valor, 2) if valor else 0


def cantidad_facturas_anuladas():
    return Factura.objects.filter(valida=False).count()


def cantidad_clientes():
    return Cliente.objects.all().count()


def cantidad_vendedores():
    return Vendedor.objects.all().count()


def cantidad_proveedores():
    return Proveedor.objects.all().count()


def cantidad_usuarios():
    return User.objects.all().count()


def cantidad_inventario_agotado():
    return InventarioReal.objects.filter(cantidad=0).count()


def cantidad_inventario_bajo_minimo():
    return InventarioReal.objects.filter(cantidad__gt=0, cantidad__lte=F('producto__minimo')).count()


def cantidad_productos():
    return Producto.objects.all().count()


def cantidad_categorias():
    return TipoProducto.objects.all().count()


def cantidad_bancos():
    return Banco.objects.all().count()


def cantidad_formas_pago():
    return FormaDePago.objects.all().count()


def cantidad_solicitudes_pendientes_clientes():
    return SolicitudCompra.objects.filter(estado=ESTADO_SOLICITUD_PENDIENTE, vendedor__isnull=True).count()


def cantidad_solicitudes_pendientes_vendedores():
    return SolicitudCompra.objects.filter(estado=ESTADO_SOLICITUD_PENDIENTE, vendedor__isnull=False).count()


def cantidad_solicitudes_asignadas():
    return SolicitudCompra.objects.filter(estado=ESTADO_SOLICITUD_ASIGNADA).count()
