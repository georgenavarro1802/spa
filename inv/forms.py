import os

from django import forms
from django.forms import DateTimeInput

from inv.models import (UnidadMedida, TipoProducto, TipoDocumento, Banco, TipoTarjetaBanco, ProcesadorPagoTarjeta,
                        FormaDePago, Area, TipoCabello, TipoPiel, TipoServicio, Producto, Servicio, Proveedor,
                        TIPOS_PAQUETES, Factura, Paquete, Cliente, Colaborador)
from spa.settings import (TIPO_CLIENTE_CORPORATIVO, TIPO_PRODUCTO_PARA_VENTA, TIPO_PRODUCTO_PARA_CONSUMO,
                          TIPO_PRODUCTO_RECIBIDO_CONSIGNACION, VALORACION_EXCELENTE, VALORACION_MUYBIEN, 
                          VALORACION_BIEN, VALORACION_REGULAR, VALORACION_MAL, PAQUETE_PROMOCIONAL, PAQUETE_SERVICIO, 
                          TIPO_CLIENTE_NORMAL, TIPO_CLIENTE_VIP)


def deshabilitar_campo(form, campo):
    form.fields[campo].widget.attrs['readonly'] = True
    form.fields[campo].widget.attrs['disabled'] = True


class ExtFileField(forms.FileField):
    """
    * max_upload_size - a number indicating the maximum file size allowed for upload.
            500Kb - 524288
            1MB - 1048576
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    t = ExtFileField(ext_whitelist=(".pdf", ".txt"), max_upload_size=)
    """

    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.ext_whitelist = [i.lower() for i in ext_whitelist]
        self.max_upload_size = kwargs.pop("max_upload_size")
        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        upload = super(ExtFileField, self).clean(*args, **kwargs)
        if upload:
            size = upload.size
            filename = upload.name
            ext = os.path.splitext(filename)[1]
            ext = ext.lower()

            if size == 0 or ext not in self.ext_whitelist or size > self.max_upload_size:
                raise forms.ValidationError("Tipo de fichero o tamanno no permitido!")


class ProductoForm(forms.Form):
    TIPOS_DESTINOS_PRODUCTO = (
        (TIPO_PRODUCTO_PARA_VENTA, 'VENTA'),
        (TIPO_PRODUCTO_PARA_CONSUMO, 'CONSUMO'),
        (TIPO_PRODUCTO_RECIBIDO_CONSIGNACION, 'RECIBIDO CONSIGNACIÓN')
    )
    tipo = forms.ChoiceField(choices=TIPOS_DESTINOS_PRODUCTO, initial=TIPO_PRODUCTO_PARA_VENTA,
                             widget=forms.Select(attrs={'class': 'imp-50', 'separador': 'Datos Generales'}))
    tipoproducto = forms.ModelChoiceField(TipoProducto.objects, label='Categoría',
                                          widget=forms.Select(attrs={'class': 'imp-50'}))
    codigo = forms.CharField(label='Código', required=False, widget=forms.TextInput(attrs={'class': 'imp-30'}))
    descripcion = forms.CharField(label='Descripción', widget=forms.Textarea({'rows': '2'}))
    unidadmedida = forms.ModelChoiceField(UnidadMedida.objects, label='UM',
                                          widget=forms.Select(attrs={'class': 'imp-30'}))
    alias = forms.CharField(max_length=20, label='Alias', required=False,
                            widget=forms.TextInput(attrs={'class': 'imp-30'}))
    codigobarra = forms.CharField(max_length=20, label='Código Barra', required=False,
                                  widget=forms.TextInput(attrs={'class': 'imp-30'}))
    minimo = forms.FloatField(initial='0.00', label='Cantidad Mínima', required=False,
                              widget=forms.TextInput(attrs={'class': 'imp-20 atright'}))
    con_iva = forms.BooleanField(initial=True, required=False, label='Con IVA?')
    precio = forms.FloatField(initial='0.00', label='Referencial', required=False,
                              widget=forms.TextInput(attrs={'class': 'imp-20 atright', 
                                                            'separador': 'Configurar Precios'}))
    precio_cliente_normal = forms.FloatField(initial='0.00', label='Clientes Normales', required=False,
                                             widget=forms.TextInput(attrs={'class': 'imp-20 atright'}))
    precio_cliente_corporativo = forms.FloatField(initial='0.00', label='Clientes Corporativos', required=False,
                                                  widget=forms.TextInput(attrs={'class': 'imp-20 atright'}))
    precio_cliente_vip = forms.FloatField(initial='0.00', label='Clientes Vip', required=False,
                                          widget=forms.TextInput(attrs={'class': 'imp-20 atright'}))

    def for_editproducto(self):
        self.fields['tipo'].widget.attrs['readonly'] = True
        self.fields['codigo'].widget.attrs['readonly'] = True
        self.fields['tipoproducto'].widget.attrs['readonly'] = True


class ServicioForm(forms.Form):
    tiposervicio = forms.ModelChoiceField(TipoServicio.objects, label='Categoría',
                                          widget=forms.Select(attrs={'class': 'imp-50'}))
    codigo = forms.CharField(label='Código', required=False, widget=forms.TextInput(attrs={'class': 'imp-30'}))
    descripcion = forms.CharField(label='Descripción', widget=forms.Textarea({'rows': '2'}))
    unidadmedida = forms.ModelChoiceField(UnidadMedida.objects, label='UM',
                                          widget=forms.Select(attrs={'class': 'imp-30'}))
    alias = forms.CharField(max_length=20, label='Alias', required=False,
                            widget=forms.TextInput(attrs={'class': 'imp-30'}))
    con_iva = forms.BooleanField(initial=True, required=False, label='Con IVA?')
    costo_estandar = forms.FloatField(initial='0.00', label='Costo estándar', required=False,
                                      widget=forms.TextInput(attrs={'class': 'imp-20 atright'}))
    precio = forms.FloatField(initial='0.00', label='Referencial', required=False,
                              widget=forms.TextInput(attrs={'class': 'imp-20 atright', 
                                                            'separador': 'Configurar Precios'}))
    precio_cliente_normal = forms.FloatField(initial='0.00', label='Clientes Normales', required=False,
                                             widget=forms.TextInput(attrs={'class': 'imp-20 atright'}))
    precio_cliente_corporativo = forms.FloatField(initial='0.00', label='Clientes Corporativos', required=False,
                                                  widget=forms.TextInput(attrs={'class': 'imp-20 atright'}))
    precio_cliente_vip = forms.FloatField(initial='0.00', label='Clientes Vip', required=False,
                                          widget=forms.TextInput(attrs={'class': 'imp-20 atright'}))

    def for_edit(self):
        self.fields['codigo'].widget.attrs['readonly'] = True
        self.fields['tiposervicio'].widget.attrs['readonly'] = True


class RecetaForm(forms.Form):
    producto = forms.ModelChoiceField(Producto.objects, label='Producto')

    def for_receta(self, servicio):
        self.fields['producto'].queryset = Producto.objects.filter(tipo=TIPO_PRODUCTO_PARA_CONSUMO).exclude(receta__servicio=servicio)


class PaqueteProductoForm(forms.Form):
    producto = forms.ModelChoiceField(Producto.objects, label='Producto',
                                      widget=forms.Select(attrs={'class': 'myselect2'}))

    def for_paquete(self, paquete):
        self.fields['producto'].queryset = Producto.objects.filter(tipo=TIPO_PRODUCTO_PARA_VENTA).exclude(paqueteproducto__paquete=paquete)


class PaqueteServicioForm(forms.Form):
    servicio = forms.ModelChoiceField(Servicio.objects, label='Servicio',
                                      widget=forms.Select(attrs={'class': 'myselect2'}))

    def for_paquete(self, paquete):
        self.fields['servicio'].queryset = Servicio.objects.all().exclude(paqueteservicio__paquete=paquete)


class ServicioFuturoForm(forms.Form):
    servicio = forms.ModelChoiceField(Servicio.objects, label='Servicio Futuro',
                                      widget=forms.Select(attrs={'class': 'myselect2'}))
    fecha = forms.DateField(label=u"Fecha", input_formats=['%d-%m-%Y'],
                            widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}))

    def for_serviciofuturo(self, orden):
        self.fields['servicio'].queryset = Servicio.objects.all().exclude(serviciofuturo__orden=orden)


class PaqueteForm(forms.Form):
    codigo = forms.CharField(label='Código', required=False,
                             widget=forms.TextInput(attrs={'class': 'imp-30'}))
    descripcion = forms.CharField(label='Descripción', widget=forms.TextInput())
    alias = forms.CharField(max_length=20, label='Alias', required=False,
                            widget=forms.TextInput(attrs={'class': 'imp-30'}))
    tipo = forms.ChoiceField(choices=TIPOS_PAQUETES, initial=PAQUETE_PROMOCIONAL,
                             widget=forms.Select(attrs={'class': 'imp-30'}))
    sesiones = forms.IntegerField(initial=2, label='Sesiones',
                                  widget=forms.TextInput(attrs={'class': 'imp-10 atright'}))


class ProveedorForm(forms.Form):
    nombre = forms.CharField(max_length=200, label='Razón Social')
    identificacion = forms.CharField(max_length=200, label='Identificación', required=False)
    alias = forms.CharField(max_length=100, label='Alias', required=False)
    pais = forms.CharField(max_length=200, label='Pais', required=False)
    direccion = forms.CharField(max_length=200, label='Dirección', required=False)
    telefono = forms.CharField(max_length=100, label='Teléfono', required=False)
    celular = forms.CharField(max_length=100, label='Celular', required=False)
    email = forms.CharField(max_length=200, label='Email', required=False)
    fax = forms.CharField(max_length=100, label='Fax', required=False)
    logo = ExtFileField(label='Seleccione Logo', required=False,
                        help_text='Tamaño Maximo permitido 2 mb, en formato jpeg, jpg, gif, png, bmp',
                        ext_whitelist=(".jpeg", ".jpg", ".gif", ".png", ".bmp"), max_upload_size=2097152)


class IngresoProductoForm(forms.Form):
    proveedor = forms.CharField()
    tipodocumento = forms.ModelChoiceField(TipoDocumento.objects, label='Tipo Documento', 
                                           widget=forms.Select(attrs={'class': 'imp-30'}))
    numerodocumento = forms.CharField(label='Número Documento', widget=forms.TextInput(attrs={'class': 'imp-30'}))
    descripcion = forms.CharField(label='Descripción')
    fechadocumento = forms.DateField(label=u"Fecha", input_formats=['%d-%m-%Y'], 
                                     widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}))


class DetalleIngresoProductoForm(forms.Form):
    codigoprod = forms.CharField(max_length=30, label='Código', widget=forms.TextInput(attrs={'class': 'imp-50'}))
    tipoprod = forms.ModelChoiceField(TipoProducto.objects, label=u"Categoría", widget=forms.Select(attrs={'class': 'imp-50'}))
    descripcionprod = forms.CharField(label='Descripción', widget=forms.Textarea({'rows': '2'}))
    unidadmedidaprod = forms.ModelChoiceField(UnidadMedida.objects, label='UM', widget=forms.Select(attrs={'class': 'imp-25'}))
    cantidadprod = forms.FloatField(initial=0.00, label='Cantidad total', widget=forms.TextInput(attrs={'class': 'imp-25 atright'}))
    costoprod = forms.FloatField(initial=0.00, label='Costo', widget=forms.TextInput(attrs={'class': 'imp-25 atright'}))
    valorprod = forms.FloatField(initial=0.00, label='Valor', widget=forms.TextInput(attrs={'class': 'imp-25 atright'}))


class ClienteForm(forms.Form):
    TIPOS_CLIENTE = (
        (TIPO_CLIENTE_NORMAL, 'NORMAL'),
        (TIPO_CLIENTE_CORPORATIVO, 'CORPORATIVO'),
        (TIPO_CLIENTE_VIP, 'VIP')
    )
    tipo = forms.ChoiceField(choices=TIPOS_CLIENTE, initial=TIPO_CLIENTE_NORMAL, 
                             widget=forms.Select(attrs={'class': 'imp-25', 'separador': 'Datos Generales'}))
    identificacion = forms.CharField(max_length=13, label='Identificación', required=False, 
                                     widget=forms.TextInput(attrs={'class': 'imp-25'}))
    nombre = forms.CharField(max_length=350, label='Nombre completo')
    domicilio = forms.CharField(label='Domicilio', required=False, 
                                widget=forms.Textarea(attrs={'cols': '1', 'rows': '2'}))
    fecha_nacimiento = forms.DateField(input_formats=['%d-%m-%Y'], required=False, label='Fecha nacimiento',  
                                       widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}))
    email = forms.CharField(max_length=100, label='Email', required=False, 
                            widget=forms.TextInput(attrs={'class': 'imp-email conlower'}))
    telefono = forms.CharField(max_length=50, label='Teléfono', required=False, 
                               widget=forms.TextInput(attrs={'class': 'imp-25'}))
    celular = forms.CharField(max_length=50, label='Celular', required=False, 
                              widget=forms.TextInput(attrs={'class': 'imp-25'}))
    usuario = forms.CharField(max_length=30, label='Usuario', required=False, 
                              widget=forms.TextInput(attrs={'class': 'imp-25 conlower'}))

    # Clientes Corporativos
    ruc = forms.CharField(max_length=13, label='RUC', required=False, 
                          widget=forms.TextInput(attrs={'class': 'imp-25', 'separador': 'Datos Corporativos', 
                                                        'separador_class': 'corporativo'}))
    razon_social = forms.CharField(max_length=350, required=False, label='Nombre compañía')
    representante_legal = forms.CharField(max_length=300, required=False, label='Representante legal')

    # Informacion adicional
    tipo_cabello = forms.ModelChoiceField(label='Tipo de cabello', queryset=TipoCabello.objects.all(), required=False, 
                                          widget=forms.Select(attrs={'class': 'imp-40',
                                                                     'separador': 'Información Específica',
                                                                     'separador_class': 'especifico'}))
    tipo_piel = forms.ModelChoiceField(label='Tipo de piel', queryset=TipoPiel.objects.all(), required=False, 
                                       widget=forms.Select(attrs={'class': 'imp-40'}))
    caracteristicas_fisicas = forms.CharField(label='Características físicas', required=False, 
                                              widget=forms.Textarea(attrs={'cols': '1', 'rows': '2'}))
    alergias = forms.CharField(label='Alergías', required=False, widget=forms.Textarea(attrs={'cols': '1', 'rows': '2'}))
    oportunidades_servicios = forms.CharField(label='Oportunidades servicios', required=False, 
                                              widget=forms.Textarea(attrs={'cols': '1', 'rows': '2'}))

    foto = ExtFileField(label='Foto', required=False,
                        help_text='Tamaño máximo 2 mb, en formatos jpeg, jpg, gif, png, bmp',
                        ext_whitelist=(".jpeg", ".jpg", ".gif", ".png", ".bmp"), max_upload_size=2097152,
                        widget=forms.FileInput(attrs={'separador': 'Foto del cliente', 'separador_class': 'foto'}))

    def editar(self):
        deshabilitar_campo(self, 'usuario')


class VendedorForm(forms.Form):
    cedula = forms.CharField(max_length=10, label='Cedula', widget=forms.TextInput(attrs={'class': 'imp-25'}))
    nombre = forms.CharField(max_length=300, label='Nombre')
    direccion = forms.CharField(max_length=300, label='Dirección', required=False)
    telefono = forms.CharField(max_length=50, label='Teléfono', required=False,
                               widget=forms.TextInput(attrs={'class': 'imp-25'}))
    email = forms.CharField(max_length=100, label='Email', required=False,
                            widget=forms.TextInput(attrs={'class': 'imp-50'}))
    usuario = forms.CharField(max_length=30, label='Usuario', required=False,
                              widget=forms.TextInput(attrs={'class': 'imp-25 conlower'}))


class CajeroForm(forms.Form):
    cedula = forms.CharField(max_length=10, label='Cedula', widget=forms.TextInput(attrs={'class': 'imp-25'}))
    nombre = forms.CharField(max_length=300, label='Nombre')
    direccion = forms.CharField(max_length=300, label='Dirección', required=False)
    telefono = forms.CharField(max_length=50, label='Teléfono', required=False,
                               widget=forms.TextInput(attrs={'class': 'imp-25'}))
    email = forms.CharField(max_length=100, label='Email', required=False,
                            widget=forms.TextInput(attrs={'class': 'imp-50'}))
    usuario = forms.CharField(max_length=30, label='Usuario', required=False,
                              widget=forms.TextInput(attrs={'class': 'imp-25 conlower'}))


class PagoForm(forms.Form):
    cliente = forms.CharField(label='Cliente')


class TransaccionPagoForm(forms.Form):
    formapago = forms.ModelChoiceField(FormaDePago.objects, label='Forma de Pago',
                                       widget=forms.Select(attrs={'class': 'imp-50'}))
    valoringreso = forms.FloatField(initial=0.00, label='Valor',
                                    widget=forms.TextInput(attrs={'class': 'imp-number atright'}))
    # Efectivo
    fechaefectivo = forms.DateField(input_formats=['%d-%m-%Y'], required=False,
                                    widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}),
                                    label='Fecha Efectivo')
    # Cheque
    fechacheque = forms.DateField(input_formats=['%d-%m-%Y'], required=False,
                                  widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}),
                                  label='Fecha Cheque')
    numerocheque = forms.CharField(label='No. Cheque', required=False,
                                   widget=forms.TextInput(attrs={'class': 'imp-25'}))
    bancocheque = forms.ModelChoiceField(Banco.objects, label='Banco Cheque',
                                         widget=forms.Select(attrs={'class': 'imp-50'}))
    emite = forms.CharField(label='Emite', widget=forms.TextInput(attrs={'class': 'imp-75'}))
    postfechado = forms.BooleanField(label='Postfechado?', required=False)
    depositado = forms.BooleanField(label='Depositado?', required=False)
    fechadepositado = forms.DateField(input_formats=['%d-%m-%Y'], required=False,
                                      widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}),
                                      label='Fecha Deposito')
    # Deposito
    fechadeposito = forms.DateField(input_formats=['%d-%m-%Y'], required=False,
                                    widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}),
                                    label='Fecha Depósito')
    numerodeposito = forms.CharField(label='No. Depósito', widget=forms.TextInput(attrs={'class': 'imp-25'}))
    # Transferencia
    fechatransferencia = forms.DateField(input_formats=['%d-%m-%Y'], required=False,
                                         widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}),
                                         label='Fecha Transferencia')
    numerotransferencia = forms.CharField(label='No. Transferencia', widget=forms.TextInput(attrs={'class': 'imp-25'}))
    efectuadopor = forms.CharField(label='Efectuado por', widget=forms.TextInput(attrs={'class': 'imp-75'}))
    # Tarjeta
    fechatarjeta = forms.DateField(input_formats=['%d-%m-%Y'], required=False,
                                   widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}),
                                   label='Fecha Tarjeta')
    referencia = forms.CharField(label='No. Autorización', widget=forms.TextInput(attrs={'class': 'imp-25'}))
    lote = forms.CharField(label='No. Lote', widget=forms.TextInput(attrs={'class': 'imp-25'}))
    bancotarjeta = forms.ModelChoiceField(Banco.objects, label='Banco Tarjeta',
                                          widget=forms.Select(attrs={'class': 'imp-50'}))
    tipotarjeta = forms.ModelChoiceField(TipoTarjetaBanco.objects, label='Tipo Tarjeta',
                                         widget=forms.Select(attrs={'class': 'imp-50'}))
    procesadorpago = forms.ModelChoiceField(ProcesadorPagoTarjeta.objects, label='Procesador Pago',
                                            widget=forms.Select(attrs={'class': 'imp-50'}))
    poseedor = forms.CharField(label='Poseedor', widget=forms.TextInput(attrs={'class': 'imp-75'}))
    # Retencion
    fecharetencion = forms.DateField(input_formats=['%d-%m-%Y'], required=False,
                                     widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}),
                                     label='Fecha Retención')
    numeroretencion = forms.CharField(label='No. Retención', widget=forms.TextInput(attrs={'class': 'imp-50'}))

    # Observaciones
    observaciones = forms.CharField(label='Observaciones',
                                    widget=forms.Textarea(attrs={'rows': '2', 'cols': '20',
                                                                 'class': 'input-block-level'}),
                                    required=False)


class FotoProductoForm(forms.Form):
    foto = ExtFileField(label='Seleccione Imagen',
                        help_text='Tamano Maximo permitido 2 mb, en formato jpeg, jpg, gif, png, bmp',
                        ext_whitelist=(".jpeg", ".jpg", ".gif", ".png", ".bmp"), max_upload_size=2097152)


class SesionCajaForm(forms.Form):
    fondo = forms.FloatField(label="Fondo Inicial", required=True, widget=forms.TextInput(attrs={'class': 'atright'}))


class CierreSesionCajaForm(forms.Form):
    bill100 = forms.IntegerField(label="Billetes de 100", required=False, widget=forms.TextInput(attrs={'class': 'imp-40 atright'}))
    bill50 = forms.IntegerField(label="Billetes de 50", required=False, widget=forms.TextInput(attrs={'class': 'imp-40 atright'}))
    bill20 = forms.IntegerField(label="Billetes de 20", required=False, widget=forms.TextInput(attrs={'class': 'imp-40 atright'}))
    bill10 = forms.IntegerField(label="Billetes de 10", required=False, widget=forms.TextInput(attrs={'class': 'imp-40 atright'}))
    bill5 = forms.IntegerField(label="Billetes de 5", required=False, widget=forms.TextInput(attrs={'class': 'imp-40 atright'}))
    bill2 = forms.IntegerField(label="Billetes de 2", required=False, widget=forms.TextInput(attrs={'class': 'imp-40 atright'}))
    bill1 = forms.IntegerField(label="Billetes de 1", required=False, widget=forms.TextInput(attrs={'class': 'imp-40 atright'}))
    enmonedas = forms.FloatField(label="En Monedas", required=False, widget=forms.TextInput(attrs={'class': 'imp-40 atright'}))
    cheque = forms.FloatField(label=u"Cheques", required=False, widget=forms.TextInput(attrs={'class': 'imp-40 atright'}))
    deposito = forms.FloatField(label=u"Depósitos", required=False, widget=forms.TextInput(attrs={'class': 'imp-40 atright'}))
    transferencia = forms.FloatField(label="Transferencia", required=False, widget=forms.TextInput(attrs={'class': 'imp-40 atright'}))
    total = forms.FloatField(label="Total", required=False, widget=forms.TextInput(attrs={'class': 'imp-40 atright'}))


class FacturaForm(forms.Form):
    cliente = forms.CharField(label='Ruc/Cedula')
    nombre = forms.CharField(max_length=200, label='Nombre')
    telefono = forms.CharField(max_length=200, label='Telefono')
    direccion = forms.CharField(max_length=200, label='Direccion')
    numero = forms.CharField(label='Num. Factura')


class DetalleFacturaForm(forms.Form):
    dcantidad = forms.IntegerField(label="Cantidad")
    detalle = forms.CharField(widget=forms.Textarea, label='Detalle')
    dpvp = forms.FloatField(initial=0.00, label='Pvp')
    dsubtotal = forms.FloatField(initial=0.00, label='Subtotal')
    diva = forms.FloatField(initial=0.00, label='Iva')
    dtotal = forms.FloatField(initial=0.00, label='Total')


class AnularFacturaForm(forms.Form):
    motivo = forms.CharField(max_length=200, label='Motivo')


class ValeCajaForm(forms.Form):
    valor = forms.FloatField(label='Valor')
    recibe = forms.CharField(label='Recibe', required=False)
    responsable = forms.CharField(label='Autoriza', required=False)
    referencia = forms.CharField(label='Referencia', required=False)
    concepto = forms.CharField(widget=forms.Textarea, label='Concepto', required=False)


class CambioClaveForm(forms.Form):
    anterior = forms.CharField(label='Clave Anterior', widget=forms.PasswordInput(attrs={'class': 'imp-75'}))
    nueva = forms.CharField(label='Nueva clave', widget=forms.PasswordInput(attrs={'class': 'imp-75'}))
    repetir = forms.CharField(label='Repetir clave', widget=forms.PasswordInput(attrs={'class': 'imp-75'}))


class DepositarForm(forms.Form):
    fechadepositado = forms.DateField(input_formats=['%d-%m-%Y'], required=False, label='Fecha Depósito',
                                      widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}))


class ChequeProtestadoForm(forms.Form):
    fecha = forms.DateField(input_formats=['%d-%m-%Y'], required=False, label='Fecha Protesto',
                            widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}))
    motivo = forms.CharField(label='Motivo', max_length=300)


class AreaForm(forms.Form):
    area = forms.ModelChoiceField(label='Nueva Area', queryset=Area.objects, widget=forms.Select())

    def excluir_area_actual(self, area):
        self.fields['area'].queryset = Area.objects.exclude(id=area.id)


class ProductoPreciosForm(forms.Form):
    cantidad_minima = forms.FloatField(initial=0.00, label='Cant. Mínima', required=False,
                                       widget=forms.TextInput(attrs={'class': 'imp-number'}))
    cantidad_maxima = forms.FloatField(initial=0.00, label='Cant. Máxima', required=False,
                                       widget=forms.TextInput(attrs={'class': 'imp-number'}))
    precio_sobre_costo = forms.BooleanField(initial=True, label='Precio sobre costo ?', required=False)
    porciento_costo = forms.FloatField(initial=0.00, label='% sobre costo', required=False,
                                       widget=forms.TextInput(attrs={'class': 'imp-number'}))
    precio_sobre_precio = forms.BooleanField(initial=False, label='Precio sobre precio ?', required=False)
    porciento_precio = forms.FloatField(initial=0.00, label='% sobre precio', required=False,
                                        widget=forms.TextInput(attrs={'class': 'imp-number'}))
    observaciones = forms.CharField(label='Observaciones', required=False,
                                    widget=forms.Textarea(attrs={'rows': '3', 'cols': 3}))


class VendedorExpedienteForm(forms.Form):
    nombre = forms.CharField(max_length=300, label='Descripción')
    archivo = ExtFileField(label='Seleccione Archivo',
                           help_text='Tamano Maximo permitido 10 mb, en formato jpeg, jpg, gif, png, bmp',
                           ext_whitelist=(".jpeg", ".jpg", ".gif", ".png", ".bmp", ".doc", ".pdf", ".docx"),
                           max_upload_size=10485760)


class VideoForm(forms.Form):
    descripcion = forms.CharField(max_length=300, label='Descripción')
    video = ExtFileField(label='Seleccione Video',
                         help_text='Tamano Maximo permitido 500 Mb, en formato mpeg, avi, mp4',
                         ext_whitelist=(".mpeg", ".avi", ".mp4"), max_upload_size=429916160)


class ImportarArchivoXLSForm(forms.Form):
    proveedor = forms.ModelChoiceField(Proveedor.objects, label='Proveedor', widget=forms.Select())
    archivo = ExtFileField(label='Seleccione Archivo', help_text='Tamaño maximo permitido 4Mb, en formato xls, xlsx',
                           ext_whitelist=(".xls", ".xlsx"), max_upload_size=4194304)


class ValoracionForm(forms.Form):
    TIPOS_VALORACIONES = (
        (VALORACION_EXCELENTE, 'EXCELENTE'),
        (VALORACION_MUYBIEN, 'MUY BIEN'),
        (VALORACION_BIEN, 'BIEN'),
        (VALORACION_REGULAR, 'REGULAR'),
        (VALORACION_MAL, 'MAL')
    )
    valoracion = forms.ChoiceField(label=u"Valoración", choices=TIPOS_VALORACIONES, required=False,
                                   initial=VALORACION_EXCELENTE, widget=forms.Select(attrs={'class': 'imp-50'}))
    recomendaciones = forms.CharField(label='Recomendaciones', required=False,
                                      widget=forms.Textarea({'rows': '2', 'cols': '2'}))


class SesionesForm(forms.Form):
    factura = forms.ModelChoiceField(Factura.objects, label='Factura', required=True,
                                     widget=forms.Select(attrs={'class': 'imp-50 myselect2'}))
    cliente = forms.ModelChoiceField(Cliente.objects, label='Cliente',
                                     widget=forms.Select(attrs={'class': 'imp-50 myselect2'}))
    paquete = forms.ModelChoiceField(Paquete.objects.exclude(tipo=PAQUETE_SERVICIO), label='Paquete',
                                     widget=forms.Select(attrs={'class': 'imp-50 myselect2'}))
    colaborador = forms.ModelChoiceField(Colaborador.objects, label='Colaborador',
                                         widget=forms.Select(attrs={'class': 'imp-50 myselect2'}))
    fecha = forms.DateField(label=u"Fecha", input_formats=['%d-%m-%Y'],
                            widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}))
    observaciones = forms.CharField(label='Observaciones', required=False,
                                    widget=forms.Textarea(attrs={'rows': '2', 'cols': '2'}))
    proxima_cita = forms.DateField(label=u"Prox.Cita", required=False, input_formats=['%d-%m-%Y'],
                                   widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}))

    def solo_facturas_con_paquetes(self):
        self.fields['factura'].queryset = Factura.objects.filter(detallefactura__paquete__isnull=False).\
            exclude(detallefactura__paquete__tipo=PAQUETE_SERVICIO).distinct()


class MisSesionesForm(forms.Form):
    cliente = forms.ModelChoiceField(Cliente.objects, label='Cliente',
                                     widget=forms.Select(attrs={'class': 'imp-50'}))
    paquete = forms.ModelChoiceField(Paquete.objects.exclude(tipo=PAQUETE_SERVICIO), label='Paquete',
                                     widget=forms.Select(attrs={'class': 'imp-50'}))
    fecha = forms.DateField(label=u"Fecha", input_formats=['%d-%m-%Y'],
                            widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}))
    observaciones = forms.CharField(label='Observaciones', required=False,
                                    widget=forms.Textarea(attrs={'rows': '2', 'cols': '2'}))
    proxima_cita = forms.DateField(label=u"Prox.Cita", required=False, input_formats=['%d-%m-%Y'],
                                   widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'selectorfecha'}))
    cerrada = forms.BooleanField(initial=False, required=False, label='Cerrar Sesión?')
