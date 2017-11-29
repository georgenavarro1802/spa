import io
import json
import math
import os
import random
from datetime import datetime
from decimal import Decimal
from html import escape

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.forms import model_to_dict
from django.http import HttpResponse
from fpdf import FPDF
from xhtml2pdf import pisa
from easy_pdf.rendering import fetch_resources

from inv import number_to_letter
from inv.models import (Cliente, Vendedor, Producto, AudiUsuarioTabla, Servicio, Paquete, Empresa)
from spa.settings import (ACCION_ADICIONAR, ACCION_MODIFICAR, ACCION_ELIMINAR, MENSAJES_ERROR, JR_USEROUTPUT_FOLDER)

UNIDADES = (
    '',
    'UN ',
    'DOS ',
    'TRES ',
    'CUATRO ',
    'CINCO ',
    'SEIS ',
    'SIETE ',
    'OCHO ',
    'NUEVE ',
    'DIEZ ',
    'ONCE ',
    'DOCE ',
    'TRECE ',
    'CATORCE ',
    'QUINCE ',
    'DIECISEIS ',
    'DIECISIETE ',
    'DIECIOCHO ',
    'DIECINUEVE ',
    'VEINTE '
)

DECENAS = (
    'VENTI',
    'TREINTA ',
    'CUARENTA ',
    'CINCUENTA ',
    'SESENTA ',
    'SETENTA ',
    'OCHENTA ',
    'NOVENTA ',
    'CIEN '
)

CENTENAS = (
    'CIENTO ',
    'DOSCIENTOS ',
    'TRESCIENTOS ',
    'CUATROCIENTOS ',
    'QUINIENTOS ',
    'SEISCIENTOS ',
    'SETECIENTOS ',
    'OCHOCIENTOS ',
    'NOVECIENTOS '
)

MONEDAS = (
    {'country': u'Colombia', 'currency': 'COP', 'singular': u'PESO COLOMBIANO', 'plural': u'PESOS COLOMBIANOS',
     'symbol': u'$'},
    {'country': u'Estados Unidos', 'currency': 'USD', 'singular': u'DÃ“LAR', 'plural': u'DÃ“LARES', 'symbol': u'US$'},
    {'country': u'Europa', 'currency': 'EUR', 'singular': u'EURO', 'plural': u'EUROS', 'symbol': u'â‚¬'},
    {'country': u'MÃ©xico', 'currency': 'MXN', 'singular': u'PESO MEXICANO', 'plural': u'PESOS MEXICANOS',
     'symbol': u'$'},
    {'country': u'PerÃº', 'currency': 'PEN', 'singular': u'NUEVO SOL', 'plural': u'NUEVOS SOLES', 'symbol': u'S/.'},
    {'country': u'Reino Unido', 'currency': 'GBP', 'singular': u'LIBRA', 'plural': u'LIBRAS', 'symbol': u'Â£'}
)

MESES_CHOICES = (
    (1, u'Enero'),
    (2, u'Febrero'),
    (3, u'Marzo'),
    (4, u'Abril'),
    (5, u'Mayo'),
    (6, u'Junio'),
    (7, u'Julio'),
    (8, u'Agosto'),
    (9, u'Septiembre'),
    (10, u'Octubre'),
    (11, u'Noviembre'),
    (12, u'Diciembre')
)


# Para definir la moneda me estoy basando en los cÃ³digo que establece el ISO 4217
# Decidi­ poner las variables en inglÃ©s, porque es mÃ¡s sencillo de ubicarlas sin importar el paÃ­s
# Si, ya sÃ© que Europa no es un paÃ­s, pero no se me ocurriÃ³ un nombre mejor para la clave.
def to_word(number, mi_moneda=None):
    if mi_moneda is not None:
        try:
            moneda = filter(lambda x: x['currency'] == mi_moneda, MONEDAS)
            if number < 2:
                moneda = moneda['singular']
            else:
                moneda = moneda['plural']
        except:
            return "Tipo de moneda invÃ¡lida"
    else:
        moneda = ""
    """Converts a number into string representation"""
    converted = ''

    if not (0 < number < 999999999):
        return 'No es posible convertir el numero a letras'

    number_str = str(number).zfill(9)
    millones = number_str[:3]
    miles = number_str[3:6]
    cientos = number_str[6:]

    if millones:
        if millones == '001':
            converted += 'UN MILLON '
        elif int(millones) > 0:
            converted += '%sMILLONES ' % __convert_group(millones)

    if miles:
        if miles == '001':
            converted += 'MIL '
        elif int(miles) > 0:
            converted += '%sMIL ' % __convert_group(miles)

    if cientos:
        if cientos == '001':
            converted += 'UN '
        elif int(cientos) > 0:
            converted += '%s ' % __convert_group(cientos)

    converted += moneda

    return converted.title()


def __convert_group(n):
    """Turn each group of numbers into letters"""
    output = ''

    if n == '100':
        output = "CIEN "
    elif n[0] != '0':
        output = CENTENAS[int(n[0]) - 1]

    k = int(n[1:])
    if k <= 20:
        output += UNIDADES[k]
    else:
        if (k > 30) & (n[2] != '0'):
            output += '%sY %s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])
        else:
            output += '%s%s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])

    return output


def enletras(x):
    entera = int(math.floor(x))
    fraccion = int((x - int(x)) * 100)
    if fraccion > 10:
        return (to_word(entera) + "con " + str(fraccion) + "/100").upper()
    return (to_word(entera) + "con 0" + str(fraccion) + "/100").upper()


def model_to_dict_safe(m, exclude=None):
    if not exclude:
        exclude = []
    d = model_to_dict(m, exclude=exclude)
    for x, y in d.items():
        if type(y) == Decimal:
            d[x] = float(y)
    return d


def dict_safe(d):
    for x, y in d.items():
        if type(y) == Decimal:
            d[x] = float(y)
    return d


# Obtener el IP desde donde se esta accediendo
def ip_client_address(request):
    try:
        # case server externo
        client_address = request.META['HTTP_X_FORWARDED_FOR']
    except:
        # case localhost o 127.0.0.1
        client_address = request.META['REMOTE_ADDR']

    return client_address


def generar_nombre(nombre, original):
    ext = ""
    if original.find(".") > 0:
        ext = original[original.rfind("."):]
    fecha = datetime.now().date()
    hora = datetime.now().time()
    return nombre + fecha.year.__str__() + fecha.month.__str__() + fecha.day.__str__() + \
           hora.hour.__str__() + hora.minute.__str__() + hora.second.__str__() + ext


# Metodo para Salvas en Tablas Auditoras - (Django LogEntry y en AudiUsuarioTabla)
def salva_auditoria(request, model, action, mensaje=''):
    user = request.user

    # Obtain client ip address
    client_address = ip_client_address(request)

    flagEntry = CHANGE
    # Elegir Tipo de Accion - Asignar Django LogEntry Action y Message correspondiente
    if action == ACCION_ADICIONAR:
        flagEntry = ADDITION
        flagMessage = 'Adicionado ' + model.__class__.__name__ + ' (' + client_address + ')'
    elif action == ACCION_MODIFICAR:
        flagEntry = CHANGE
        flagMessage = 'Modificado ' + model.__class__.__name__ + ' (' + client_address + ')'
    elif action == ACCION_ELIMINAR:
        flagEntry = DELETION
        flagMessage = 'Eliminado ' + model.__class__.__name__ + ' (' + client_address + ')'
    else:
        flagMessage = mensaje + ' (' + client_address + ')'

    # Registro en tabla Auditora BD
    auditusuariotabla = AudiUsuarioTabla(usuario=user,
                                         tabla=model.__class__.__name__,
                                         registroid=model.id,
                                         accion=action,
                                         fecha=datetime.now().date(),
                                         hora=datetime.now().time(),
                                         estacion=client_address)
    auditusuariotabla.save()

    # Registro en Django LogEntry
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(model).pk,
        object_id=model.id,
        object_repr=model.__str__(),
        action_flag=flagEntry,
        change_message=flagMessage
    )


class MiPaginador(Paginator):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, rango=5):
        super(MiPaginador, self).__init__(object_list, per_page, orphans=orphans,
                                          allow_empty_first_page=allow_empty_first_page)
        self.rango = rango
        self.paginas = []
        self.primera_pagina = False
        self.ultima_pagina = False

    def rangos_paginado(self, pagina):
        left = pagina - self.rango
        right = pagina + self.rango
        if left < 1:
            left = 1
        if right > self.num_pages:
            right = self.num_pages
        self.paginas = range(left, right + 1)
        self.primera_pagina = True if left > 1 else False
        self.ultima_pagina = True if right < self.num_pages else False
        self.ellipsis_izquierda = left - 1
        self.ellipsis_derecha = right + 1


def convertir_cadena_hora(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f").time()


def convertir_hora_cadena(h):
    return h.strftime("%Y-%m-%dT%H:%M:%S.%f")


def representacion_factura_str(x):
    return fix_factura_str(model_to_dict(x, exclude='fecha'), x)


def fix_factura_str(obj, f):
    obj['fecha'] = f.fecha.strftime("%d-%m-%Y")
    obj['cliente'] = model_to_dict(Cliente.objects.get(pk=obj['cliente']))
    if obj['vendedor']:
        obj['vendedor'] = model_to_dict(Vendedor.objects.get(pk=obj['vendedor']))
    obj['enletras'] = number_to_letter.enletras(obj['total'])
    obj['detalles'] = [model_to_dict(x) for x in f.mis_detalles()]
    return obj


def fix_productos_str(x):
    producto = Producto.objects.get(pk=x)
    return producto.nombre_factura()


def fix_servicios_str(x):
    servicio = Servicio.objects.get(pk=x)
    return servicio.nombre_factura()


def fix_paquetes_str(x):
    paquete = Paquete.objects.get(pk=x)
    return paquete.nombre_factura()


def mensaje_excepcion(mensaje):
    if mensaje not in MENSAJES_ERROR:
        mensaje = MENSAJES_ERROR[0]
    return mensaje


def url_back(request, mensaje=None):
    url = request.META['HTTP_REFERER'].split('/')[-1:][0]
    if 'mensj=' in url:
        url = url[:(url.find('mensj') - 1)]
    if mensaje:
        if '?' in url:
            url += "&mensj=" + mensaje
        else:
            url += "?mensj=" + mensaje
    return url


def bad_json(mensaje=None, error=None, extradata=None):
    data = {'result': 'bad'}
    if mensaje:
        data.update({'mensaje': mensaje})
    if error >= 0:
        if error == 0:
            data.update({"mensaje": "Solicitud incorrecta."})
        elif error == 1:
            data.update({"mensaje": "Error al guardar los datos."})
        elif error == 2:
            data.update({"mensaje": "Error al modificar los datos."})
        elif error == 3:
            data.update({"mensaje": "Error al eliminar los datos."})
        elif error == 4:
            data.update({"mensaje": "No tiene permisos para realizar esta acción."})
        elif error == 5:
            data.update({"mensaje": "Error al generar la información."})
        else:
            data.update({"mensaje": "Error en el sistema."})
    if extradata:
        data.update(extradata)
    return HttpResponse(json.dumps(data), content_type="application/json")


def ok_json(data=None, simple=None):
    if data:
        if not simple:
            if 'result' not in data.keys():
                data.update({"result": "ok"})
    else:
        data = {"result": "ok"}
    return HttpResponse(json.dumps(data), content_type="application/json")


def empty_json(data):
    if 'result' not in data.keys():
        data.update({"result": "ok"})
    return HttpResponse(json.dumps(data), content_type="application/json")


def generar_pdf(html, save_in_file=False):
    """ Función interna para generar pdf por método get """
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.StringIO(html), dest=result, link_callback=fetch_resources)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        if save_in_file:
            response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
        result.close()
        pisa.log.removeHandler(pisa.log.handlers)
        return response
    return HttpResponse('Existen algunos errores<pre>%s</pre>' % escape(html))


def get_pdf_factura(factura, empresaid, usuario):
    empresa = Empresa.objects.get(pk=empresaid)
    params = empresa.parametros()
    invoice = representacion_factura_str(factura)
    fecha = invoice['fecha']
    pdf = FPDF()
    # pdf.compress = False
    pdf.add_page(orientation=params.orientacion)
    pdf.set_font(params.fuente_tipo, '', params.fuente_tamano)
    pdf.text(params.factura_fecha_x, params.factura_fecha_y, fecha)
    pdf.text(params.cliente_telefono_x, params.cliente_telefono_y, invoice['cliente']['telefono'])

    if len(invoice['cliente']['nombre']) < 50:
        pdf.text(params.cliente_nombre_x, params.cliente_nombre_y, invoice['cliente']['nombre'])
    else:
        pdf.text(params.cliente_nombre_x1, params.cliente_nombre_y1, invoice['cliente']['nombre'][:51] + ' - ')
        pdf.text(params.cliente_nombre_x2, params.cliente_nombre_y2, invoice['cliente']['nombre'][51:])

    if len(invoice['cliente']['domicilio']) < 50:
        pdf.text(params.cliente_direccion_x, params.cliente_direccion_y, invoice['cliente']['domicilio'])
    else:
        pdf.text(params.cliente_direccion_x1, params.cliente_direccion_y1, invoice['cliente']['domicilio'][:51] + ' - ')
        pdf.text(params.cliente_direccion_x2, params.cliente_direccion_y2, invoice['cliente']['domicilio'][51:])

    pdf.text(params.cliente_ruc_x, params.cliente_ruc_y, invoice['cliente']['identificacion'])

    i = 0
    for detalle in invoice['detalles']:
        pdf.text(params.cantidad_x, params.cantidad_y + (i * 5), str(int(detalle['cantidad'])))
        if detalle['valor_descuento']:
            pdf.text(params.cantidad_x + 2, params.cantidad_y + (i * 5), "(*)")
        if detalle['producto']:
            pdf.text(params.producto_x, params.producto_y + (i * 5), fix_productos_str(detalle['producto']))
        elif detalle['servicio']:
            pdf.text(params.producto_x, params.producto_y + (i * 5), fix_servicios_str(detalle['servicio']))
        else:
            pdf.text(params.producto_x, params.producto_y + (i * 5), fix_paquetes_str(detalle['paquete']))
        pdf.text(params.precio_x, params.precio_y + (i * 5), "$ {}".format(detalle['precio']))
        pdf.text(params.valor_x, params.valor_y + (i * 5), "$ {}".format(detalle['valor']))
        i += 1

    pdf.text(params.factura_enletras_x, params.factura_enletras_y, invoice['enletras'])
    pdf.text(params.factura_subtotal_x, params.factura_subtotal_y, "$ {}".format(invoice['subtotal']))
    pdf.text(params.factura_iva_x, params.factura_iva_y, "$ {}".format(invoice['iva']))
    pdf.text(params.factura_total_x, params.factura_total_y, "$ {}".format(invoice['total']))

    pdfname = 'factura' + invoice['numero'] + '_' + datetime.now().date().strftime('%Y%m%d_%H%M%S') + '.pdf'
    output_folder = os.path.join(JR_USEROUTPUT_FOLDER, usuario)
    try:
        os.makedirs(output_folder)
    except:
        pass
    pdf.output(os.path.join(output_folder, pdfname))

    return pdfname


def create_username(nombre):
    array_nombre = nombre.lower().split(' ')
    if len(array_nombre) > 1:
        username = array_nombre[0][0] + array_nombre[1]
    else:
        username = array_nombre[0]
    if User.objects.filter(username__iexact=username).exists():
        username += str(random.choice(range(10, 90)))
        return create_username(username)
    return username.lower()


def get_codigo_producto(tipo, categoria):
    codigo = "P{}-{}-0001".format(tipo, categoria.codigo)
    ultimo_producto = categoria.get_ultimo_producto()
    if ultimo_producto:
        codigo = "P{}-{}-{}".format(tipo, categoria.codigo, str(ultimo_producto.secuencia_codigo() + 1).zfill(4))
    return codigo
