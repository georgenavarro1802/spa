import os
from datetime import datetime, timedelta

import math
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.aggregates import Sum

from spa.settings import (STATIC_URL, PORCIENTO_COMISION, ESTADO_SOLICITUD_APROBADA, NUMERO_DIAS_ANULAR_FACTURAS,
                          ESTADO_SOLICITUD_PENDIENTE, ESTADO_SOLICITUD_DENEGADA, ESTADO_SOLICITUD_ASIGNADA,
                          TIPO_CLIENTE_NORMAL, TIPO_CLIENTE_CORPORATIVO, TIPO_CLIENTE_VIP, TIPO_PRODUCTO_PARA_VENTA,
                          TIPO_PRODUCTO_PARA_CONSUMO, TIPO_PRODUCTO_RECIBIDO_CONSIGNACION, ACCION_ADICIONAR, 
                          VALORACION_MAL, VALORACION_REGULAR, VALORACION_BIEN, VALORACION_MUYBIEN, 
                          VALORACION_EXCELENTE, TIPO_MOVIMIENTO_ENTRADA, TIPO_MOVIMIENTO_SALIDA, PAQUETE_PROMOCIONAL, 
                          PAQUETE_MULTISESION, PAQUETE_SERVICIO)


# BEGIN MODELS MTTO
class Provincia(models.Model):
    nombre = models.CharField(max_length=200)
    latitud = models.FloatField(default=0)
    longitud = models.FloatField(default=0)

    def __str__(self):
        return "%s" % self.nombre

    class Meta:
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'
        unique_together = ('nombre', )
        ordering = ('nombre',)

    def mis_cantones(self):
        return self.canton_set.all()


class Canton(models.Model):
    provincia = models.ForeignKey(Provincia)
    nombre = models.CharField(max_length=200)
    latitud = models.FloatField(default=0)
    longitud = models.FloatField(default=0)

    def __str__(self):
        return "%s" % self.nombre

    class Meta:
        verbose_name = 'Canton'
        verbose_name_plural = 'Cantones'
        unique_together = ('provincia', 'nombre')
        ordering = ('provincia', 'nombre')


class Empresa(models.Model):
    ruc = models.CharField(max_length=13, blank=True, null=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    responsable = models.CharField(max_length=200, blank=True, null=True)
    convencional = models.CharField(max_length=10, blank=True, null=True)
    celular = models.CharField(max_length=10, blank=True, null=True)
    logo = models.FileField(upload_to='logos/%Y/%m/%d', blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        unique_together = ('ruc', )
        ordering = ('nombre', )

    def nombre_con_responsable(self):
        return "{} - {}".format(self.nombre, self.responsable)

    def download_logo(self):
        return self.logo.url

    @staticmethod
    def flexbox_query(q):
        return Empresa.objects.filter(Q(ruc__contains=q) | Q(nombre__contains=q) | Q(direccion__contains=q))

    def flexbox_repr(self):
        return self.nombre

    def flexbox_alias(self):
        return self.nombre

    def parametros(self):
        if self.parametrosempresa_set.exists():
            param = self.parametrosempresa_set.all()[0]
        else:
            param = ParametrosEmpresa(empresa=self)
            param.save()
        return param

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.id:
            self.parametros()
        super(Empresa, self).save(force_insert, force_update, using)


class ParametrosEmpresa(models.Model):
    TIPOS_ORIENTACION = (
        ("LANDSCAPE", "LANDSCAPE"),
        ("PORTRAIT", "PORTRAIT")
    )
    empresa = models.ForeignKey(Empresa)
    orientacion = models.CharField(max_length=20, choices=TIPOS_ORIENTACION, default="LANDSCAPE")
    fuente_tipo = models.CharField(max_length=20, default='courier')
    fuente_tamano = models.IntegerField(default=11)
    factura_numero_x = models.IntegerField(default=200)
    factura_numero_y = models.IntegerField(default=5)
    factura_fecha_x = models.IntegerField(default=210)
    factura_fecha_y = models.IntegerField(default=15)
    # Datos del cliente
    cliente_telefono_x = models.IntegerField(default=210)
    cliente_telefono_y = models.IntegerField(default=22)
    cliente_ciudad_x = models.IntegerField(default=210)
    cliente_ciudad_y = models.IntegerField(default=29)
    cliente_nombre_x = models.IntegerField(default=50)
    cliente_nombre_y = models.IntegerField(default=15)
    cliente_nombre_x1 = models.IntegerField(default=50)
    cliente_nombre_y1 = models.IntegerField(default=14)
    cliente_nombre_x2 = models.IntegerField(default=50)
    cliente_nombre_y2 = models.IntegerField(default=17)
    cliente_direccion_x = models.IntegerField(default=50)
    cliente_direccion_y = models.IntegerField(default=22)
    cliente_direccion_x1 = models.IntegerField(default=50)
    cliente_direccion_y1 = models.IntegerField(default=21)
    cliente_direccion_x2 = models.IntegerField(default=50)
    cliente_direccion_y2 = models.IntegerField(default=24)
    cliente_ruc_x = models.IntegerField(default=50)
    cliente_ruc_y = models.IntegerField(default=29)
    # Detalle de Factura
    cantidad_x = models.IntegerField(default=20)
    cantidad_y = models.IntegerField(default=44)
    producto_x = models.IntegerField(default=40)
    producto_y = models.IntegerField(default=44)
    precio_x = models.IntegerField(default=225)
    precio_y = models.IntegerField(default=44)
    valor_x = models.IntegerField(default=270)
    valor_y = models.IntegerField(default=44)
    # Factura Valores
    factura_enletras_x = models.IntegerField(default=20)
    factura_enletras_y = models.IntegerField(default=125)
    factura_subtotal_x = models.IntegerField(default=270)
    factura_subtotal_y = models.IntegerField(default=125)
    factura_iva_x = models.IntegerField(default=270)
    factura_iva_y = models.IntegerField(default=141)
    factura_total_x = models.IntegerField(default=270)
    factura_total_y = models.IntegerField(default=146)

    def __str__(self):
        return "{} - {} {}".format(self.empresa.nombre, self.fuente_tipo, self.fuente_tamano)

    class Meta:
        verbose_name = 'Empresa - Parametro'
        verbose_name_plural = 'Empresas - Parametros'
        unique_together = ('empresa', )
        ordering = ('empresa', )


class Video(models.Model):
    descripcion = models.CharField(max_length=300)
    file = models.FileField(upload_to='videos/', blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
        ordering = ('-fecha',)

    def download_video(self):
        return self.file.url


class TipoIdentificacion(models.Model):
    nombre = models.CharField(max_length=200)
    alias = models.CharField(max_length=1)

    def __str__(self):
        return "%s %s" % (self.nombre, self.alias)

    class Meta:
        verbose_name = 'Tipo de Identificacion'
        verbose_name_plural = 'Tipos de Identificaciones'
        unique_together = ('nombre', )
        ordering = ('nombre', )

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.alias = self.alias.upper()
        super(TipoIdentificacion, self).save(force_insert, force_update, using)


class TipoCabello(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return "%s" % self.nombre

    class Meta:
        verbose_name = 'Tipo de Cabello'
        verbose_name_plural = 'Tipos de Cabellos'
        unique_together = ('nombre', )
        ordering = ('nombre',)

    def mis_clientes(self):
        return self.cliente_set.all()


class TipoPiel(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return "%s" % self.nombre

    class Meta:
        verbose_name = 'Tipo de Piel'
        verbose_name_plural = 'Tipos de Piel'
        unique_together = ('nombre', )
        ordering = ('nombre',)

    def mis_clientes(self):
        return self.cliente_set.all()


class Proveedor(models.Model):
    nombre = models.CharField(max_length=300)
    alias = models.CharField(max_length=100, blank=True, null=True)
    identificacion = models.CharField(max_length=200, blank=True, null=True)
    direccion = models.CharField(max_length=300, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=100, blank=True, null=True)
    celular = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    fax = models.CharField(max_length=100, blank=True, null=True)
    logo = models.FileField(upload_to='fotos/%Y/%m/%d', blank=True, null=True)

    def __str__(self):
        return "%s" % self.nombre

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        unique_together = ('identificacion', )
        ordering = ('nombre', )

    @staticmethod
    def flexbox_query(q):
        return Proveedor.objects.filter(Q(nombre__contains=q) | Q(alias__contains=q) | Q(identificacion__contains=q))

    def flexbox_repr(self):
        return self.nombre_simple()

    def flexbox_alias(self):
        return self.nombre_simple()

    def nombre_simple(self):
        return self.nombre

    def nombre_identificacion(self):
        return "{} - {}".format(self.identificacion, self.nombre)

    def download_logo(self):
        if self.logo:
            return self.logo.url
        return None

    def valor_compras(self):
        valor = self.ingresoproducto_set.aggregate(suma=Sum('valor'))['suma']
        return round(valor, 2) if valor else 0

    def valor_compras_fechas(self, inicio, fin):
        valor = self.ingresoproducto_set.filter(fecha__range=(inicio, fin)).aggregate(suma=Sum('valor'))['suma']
        return round(valor, 2) if valor else 0

    def valor_fob_compras(self):
        valor = self.ingresoproducto_set.aggregate(suma=Sum('valorfob'))['suma']
        return round(valor, 2) if valor else 0

    def en_uso(self):
        return self.ingresoproducto_set.exists()

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super(Proveedor, self).save(force_insert, force_update, using)


class TipoProducto(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, blank=True, null=True)
    orden = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Producto'
        verbose_name_plural = 'Tipos de Productos'
        unique_together = ('nombre', )
        ordering = ('orden', )

    def nombre_completo(self):
        return '{} - {}'.format(self.codigo, self.nombre)

    def cantidad_productos(self):
        return InventarioReal.objects.filter(producto__tipoproducto=self,
                                             producto__tipo=TIPO_PRODUCTO_PARA_VENTA,
                                             cantidad__gt=0).distinct().count()

    def productos_con_existencias(self):
        return InventarioReal.objects.filter(producto__tipoproducto=self,
                                             producto__tipo=TIPO_PRODUCTO_PARA_VENTA,
                                             cantidad__gt=0).distinct().order_by('producto__orden')

    def tiene_productos_asociados(self):
        return self.producto_set.exists()

    def get_ultimo_producto(self):
        if self.tiene_productos_asociados():
            return self.producto_set.latest('id')
        return None

    def cantidad_paginas_catalogo(self):
        return int(math.ceil(self.cantidad_productos() / 12.0))

    @staticmethod
    def flexbox_query(q):
        return TipoProducto.objects.filter(Q(nombre__contains=q) | Q(codigo__contains=q))

    def flexbox_repr(self):
        return "%s - %s " % (self.codigo, self.nombre)

    def flexbox_alias(self):
        return [self.codigo, self.nombre]

    def valor_ventas(self):
        valor = Producto.objects.filter(tipoproducto=self, detallefactura__isnull=False,
                                        detallefactura__factura__valida=True).distinct().\
            aggregate(suma=Sum('detallefactura__valor'))['suma']
        return round(valor, 2) if valor else 0

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.nombre:
            self.nombre = self.nombre.upper()
        if self.codigo:
            self.codigo = self.codigo.upper()
        super(TipoProducto, self).save(force_insert, force_update, using)


class TipoServicio(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, blank=True, null=True)
    orden = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo de Servicio'
        verbose_name_plural = 'Tipos de Servicios'
        unique_together = ('nombre', )
        ordering = ('orden', )

    def nombre_completo(self):
        return '{} - {}'.format(self.codigo, self.nombre)

    def cantidad_servicios(self):
        return self.servicio_set.filter(activo=True).count()

    def tiene_servicios_asociados(self):
        return self.servicio_set.exists()

    def get_ultimo_servicio(self):
        if self.tiene_servicios_asociados():
            return self.servicio_set.latest('id')
        return None

    @staticmethod
    def flexbox_query(q):
        return TipoServicio.objects.filter(Q(nombre__contains=q) | Q(codigo__contains=q))

    def flexbox_repr(self):
        return "%s - %s " % (self.codigo, self.nombre)

    def flexbox_alias(self):
        return [self.codigo, self.nombre]

    def valor_ventas(self):
        valor = Servicio.objects.filter(tiposervicio=self, detallefactura__isnull=False,
                                        detallefactura__factura__valida=True).distinct().\
            aggregate(suma=Sum('detallefactura__valor'))['suma']
        return round(valor, 2) if valor else 0

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.nombre:
            self.nombre = self.nombre.upper()
        if self.codigo:
            self.codigo = self.codigo.upper()
        super(TipoServicio, self).save(force_insert, force_update, using)


class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Unidad de Medida"
        verbose_name_plural = "Unidades de Medida"
        unique_together = ('nombre', )
        ordering = ('nombre',)

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.nombre:
            self.nombre = self.nombre.upper()
        super(UnidadMedida, self).save(force_insert, force_update, using)


class Area(models.Model):
    nombre = models.CharField(max_length=100)
    es_principal = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Area"
        verbose_name_plural = "Areas"
        unique_together = ('nombre', )
        ordering = ('nombre', )


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return "[{}] {}".format(self.codigo, self.nombre)

    class Meta:
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documentos'
        unique_together = ('nombre', )
        ordering = ('codigo', 'nombre')


class Vendedor(models.Model):
    cedula = models.CharField(max_length=10)
    nombre = models.CharField(max_length=300)
    direccion = models.CharField(max_length=300, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    usuario = models.ForeignKey(User, blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.cedula, self.nombre)

    class Meta:
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"
        ordering = ('nombre', )

    @staticmethod
    def flexbox_query(q):
        return Vendedor.objects.filter(Q(nombre__contains=q) | Q(cedula__contains=q))

    def flexbox_repr(self):
        return "{} - {}".format(self.cedula, self.nombre)

    def flexbox_alias(self):
        return [self.cedula, self.nombre, self.direccion, self.telefono, self.email, self.usuario.username]

    def facturas(self):
        return self.factura_set.filter(valida=True)

    def facturas_pagadas(self):
        return self.factura_set.filter(valida=True, cancelada=True)

    def facturas_pendientes(self):
        return self.factura_set.filter(valida=True, cancelada=False)

    def cantidad_ventas(self):
        return self.factura_set.filter(valida=True).count()

    def valor_ventas(self):
        valor = self.factura_set.filter(valida=True).aggregate(suma=Sum('total'))['suma']
        return round(valor, 2) if valor else 0

    def comision_ventas(self):
        return self.valor_ventas() * PORCIENTO_COMISION  # 5% comision

    def valor_pagos(self):
        valor = self.factura_set.filter(valida=True).aggregate(suma=Sum('pagado'))['suma']
        return round(valor, 2) if valor else 0

    def valor_pendiente(self):
        return self.valor_ventas() - self.valor_pagos()

    def en_uso(self):
        return self.factura_set.exists()

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super(Vendedor, self).save(force_insert, force_update, using)


class Cliente(models.Model):
    TIPOS_CLIENTE = (
        (TIPO_CLIENTE_NORMAL, 'N'),
        (TIPO_CLIENTE_CORPORATIVO, 'C'),
        (TIPO_CLIENTE_VIP, 'V')
    )
    tipo = models.IntegerField(choices=TIPOS_CLIENTE, default=TIPO_CLIENTE_NORMAL)
    identificacion = models.CharField(max_length=13, blank=True, null=True)
    nombre = models.CharField(max_length=350)
    domicilio = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    celular = models.CharField(max_length=50, blank=True, null=True)

    # Clientes Corporativos
    ruc = models.CharField(max_length=13, blank=True, null=True)
    razon_social = models.CharField(max_length=350, blank=True, null=True)
    representante_legal = models.CharField(max_length=300, blank=True, null=True)

    # clientes corporativos y vip
    alergias = models.TextField(blank=True, null=True)
    caracteristicas_fisicas = models.TextField(blank=True, null=True)
    tipo_cabello = models.ForeignKey(TipoCabello, blank=True, null=True)
    tipo_piel = models.ForeignKey(TipoPiel, blank=True, null=True)
    oportunidades_servicios = models.TextField(blank=True, null=True)
    foto = models.FileField(upload_to='clientes/%Y/%m/%d', blank=True, null=True)

    usuario = models.ForeignKey(User, blank=True, null=True)

    def __str__(self):
        return "{}".format(self.nombre)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ('nombre',)

    @staticmethod
    def flexbox_query(q):
        return Cliente.objects.filter(Q(nombre__contains=q) | Q(ruc__contains=q))

    def flexbox_repr(self):
        return "{}".format(self.nombre)

    def flexbox_alias(self):
        return [self.identificacion, self.nombre, self.domicilio, self.telefono, self.celular, self.email]

    def valor_ventas(self):
        valor = self.factura_set.filter(valida=True).distinct().aggregate(suma=Sum('total'))['suma']
        return round(valor, 2) if valor else 0

    def mi_cumpleannos(self):
        hoy = datetime.now().date()
        nacimiento = self.fecha_nacimiento
        if nacimiento.day == hoy.day and nacimiento.month == hoy.month:
            return True
        return False

    def edad(self):
        hoy = datetime.now().date()
        try:
            nac = self.fecha_nacimiento
            if hoy.year > nac.year:
                edad = hoy.year - nac.year
                if hoy.month <= nac.month:
                    if hoy.month == nac.month:
                        if hoy.day < nac.day:
                            edad -= 1
                    else:
                        edad -= 1
                return edad
            else:
                raise Exception

        except Exception:
            return 0

    def en_uso(self):
        return self.factura_set.exists()

    def download_foto(self):
        if self.foto:
            return self.foto.url
        return ''

    def mi_telefono(self):
        if self.telefono:
            return self.telefono
        elif self.celular:
            return self.celular
        else:
            return ""

    def mis_servicios_futuros(self):
        return self.serviciofuturo_set.all()

    def cantidad_facturas_vencidas(self):
        return self.factura_set.filter(valida=True,
                                       cancelada=False,
                                       fecha_vencimiento__lt=datetime.now().date()).count()

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super(Cliente, self).save(force_insert, force_update, using)


class Cajero(models.Model):
    cedula = models.CharField(max_length=10)
    nombre = models.CharField(max_length=300)
    direccion = models.CharField(max_length=300, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    usuario = models.ForeignKey(User, blank=True, null=True)
    area = models.ForeignKey(Area, blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.cedula, self.nombre)

    class Meta:
        verbose_name = "Cajero"
        verbose_name_plural = "Cajeros"
        unique_together = ('cedula', )
        ordering = ('nombre', )

    @staticmethod
    def flexbox_query(q):
        return Cajero.objects.filter(Q(nombre__contains=q) | Q(cedula__contains=q))

    def flexbox_repr(self):
        return self.__str__()

    def flexbox_alias(self):
        return [self.cedula, self.nombre, self.direccion, self.telefono, self.email, self.usuario.username]

    def tiene_sesioncaja_abierta(self):
        return self.sesioncaja_set.filter(abierta=True).exists()

    def get_sesion_caja_abierta(self):
        if self.tiene_sesioncaja_abierta():
            return self.sesioncaja_set.filter(abierta=True)[0]
        return None

    def sesiones_caja(self):
        return self.sesioncaja_set.all()

    def facturas(self):
        return self.factura_set.filter(valida=True)

    def facturas_pagadas(self):
        return self.factura_set.filter(valida=True, cancelada=True)

    def facturas_pendientes(self):
        return self.factura_set.filter(valida=True, cancelada=False)

    def cantidad_ventas(self):
        return self.factura_set.filter(valida=True).count()

    def valor_ventas(self):
        valor = self.factura_set.filter(valida=True).aggregate(suma=Sum('total'))['suma']
        return round(valor, 2) if valor else 0

    def comision_ventas(self):
        return self.valor_ventas() * PORCIENTO_COMISION  # 5% comision

    def valor_pagos(self):
        valor = self.factura_set.filter(valida=True).aggregate(suma=Sum('pagado'))['suma']
        return round(valor, 2) if valor else 0

    def valor_pendiente(self):
        return self.valor_ventas() - self.valor_pagos()

    def en_uso(self):
        return self.factura_set.exists()

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super(Cajero, self).save(force_insert, force_update, using)


class Colaborador(models.Model):
    cedula = models.CharField(max_length=10)
    nombre = models.CharField(max_length=300)
    direccion = models.CharField(max_length=300, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    usuario = models.ForeignKey(User, blank=True, null=True)
    area = models.ForeignKey(Area, blank=True, null=True)
    porciento_comision_serv = models.FloatField(default=0)
    porciento_comision_prod = models.FloatField(default=0)
    codigo = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.cedula, self.nombre)

    class Meta:
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaborador"
        unique_together = ('cedula', )
        ordering = ('nombre', )

    @staticmethod
    def flexbox_query(q):
        return Colaborador.objects.filter(Q(nombre__contains=q) | Q(cedula__contains=q))

    def flexbox_repr(self):
        return self.__str__()

    def flexbox_alias(self):
        return [self.cedula, self.nombre, self.direccion, self.telefono, self.email, self.usuario.username]

    def facturas(self):
        return self.detallefactura_set.filter(factura__valida=True)

    def facturas_pagadas(self):
        return self.detallefactura_set.filter(factura__valida=True, cancelada=True)

    def facturas_pendientes(self):
        return self.detallefactura_set.filter(factura__valida=True, cancelada=False)

    def cantidad_ventas(self):
        return self.detallefactura_set.filter(factura__valida=True).count()

    def valor_ventas(self):
        valor = self.detallefactura_set.filter(factura__valida=True).aggregate(suma=Sum('factura__total'))['suma']
        return round(valor, 2) if valor else 0

    def valor_ventas_sin_iva(self):
        valor = self.detallefactura_set.filter(factura__valida=True).aggregate(suma=Sum('factura__subtotal'))['suma']
        return round(valor, 2) if valor else 0

    def comision_ventas(self):
        coeficiente_serv = round(self.porciento_comision_serv / 100.0, 2)
        coeficiente_prod = round(self.porciento_comision_prod / 100.0, 2)
        return (self.valor_ventas_sin_iva() * coeficiente_serv) + (self.valor_ventas_sin_iva() * coeficiente_prod)

    def valor_pagos(self):
        valor = self.detallefactura_set.filter(factura__valida=True).aggregate(suma=Sum('factura__pagado'))['suma']
        return round(valor, 2) if valor else 0

    def valor_pendiente(self):
        return self.valor_ventas() - self.valor_pagos()

    def en_uso(self):
        return self.detallefactura_set.exists()

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super(Colaborador, self).save(force_insert, force_update, using)


# Models para gestion de PAGOS de facturas
class FormaDePago(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Forma de Pago"
        verbose_name_plural = "Formas de Pagos"
        unique_together = ('nombre', )
        ordering = ('id', )

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.nombre = self.nombre.upper()
        super(FormaDePago, self).save(force_insert, force_update, using)


class Banco(models.Model):
    nombre = models.CharField(max_length=100)
    tasaprotesto = models.FloatField(default=0)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Banco"
        verbose_name_plural = "Bancos"
        unique_together = ('nombre', )
        ordering = ('nombre', )

    @staticmethod
    def flexbox_query(q):
        return Banco.objects.filter(nombre__icontains=q).order_by('nombre')

    def flexbox_repr(self):
        return self.nombre

    def flexbox_alias(self):
        return self.nombre

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.nombre = self.nombre.upper()
        super(Banco, self).save(force_insert, force_update, using)


class TipoTarjetaBanco(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo de Tarjeta bancaria"
        verbose_name_plural = "Tipos de Tarjetas bancarias"
        unique_together = ('nombre', )
        ordering = ('nombre', )

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.nombre = self.nombre.upper()
        super(TipoTarjetaBanco, self).save(force_insert, force_update, using)


class ProcesadorPagoTarjeta(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Procesador de Pago"
        verbose_name_plural = "Procesadores de Pago"
        unique_together = ('nombre', )
        ordering = ('nombre', )

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.nombre = self.nombre.upper()
        super(ProcesadorPagoTarjeta, self).save(force_insert, force_update, using)

# END MODELS MTTO


# MODELS APP
class Producto(models.Model):
    TIPOS_DESTINOS_PRODUCTO = (
        (TIPO_PRODUCTO_PARA_VENTA, 'V'),
        (TIPO_PRODUCTO_PARA_CONSUMO, 'C'),
        (TIPO_PRODUCTO_RECIBIDO_CONSIGNACION, 'VC')
    )
    tipo = models.IntegerField(choices=TIPOS_DESTINOS_PRODUCTO, default=TIPO_PRODUCTO_PARA_VENTA)
    codigo = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    unidadmedida = models.ForeignKey(UnidadMedida)
    tipoproducto = models.ForeignKey(TipoProducto)
    precio = models.FloatField(default=0)
    precio_cliente_normal = models.FloatField(default=0)
    precio_cliente_corporativo = models.FloatField(default=0)
    precio_cliente_vip = models.FloatField(default=0)
    favorito = models.BooleanField(default=False)
    foto = models.FileField(upload_to='fotos/%Y/%m/%d', blank=True, null=True)
    alias = models.CharField(max_length=60, blank=True, null=True)
    codigobarra = models.CharField(max_length=30, blank=True, null=True)
    minimo = models.FloatField(default=0, blank=True, null=True)
    orden = models.IntegerField(default=0)
    con_iva = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    marca = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.codigo, self.descripcion)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        unique_together = ('codigo', )
        ordering = ('codigo',)

    def nombre_corto(self):
        return "{} - {}".format(self.codigo, self.descripcion)

    def nombre_factura(self):
        return "{} - {}".format(self.codigo, self.descripcion)[:70]

    def secuencia_codigo(self):
        return int(self.codigo.split("-")[2])

    def get_tipo(self):
        return "PRODUCTO"

    @staticmethod
    def flexbox_query(q):
        return Producto.objects.filter(Q(codigo__contains=q) | Q(descripcion__contains=q) | Q(alias__contains=q))

    def flexbox_repr(self):
        return "{} - {}".format(self.codigo, self.descripcion)

    def flexbox_alias(self):
        return [self.codigo, self.descripcion, self.unidadmedida.id, self.tipoproducto.id, str(self.precio),
                self.tipoproducto.nombre, self.tipo]

    def download_foto(self):
        if self.foto:
            return self.foto.url
        return STATIC_URL + 'images/prod_avatar.png'

    def inventario(self):
        if self.inventarioreal_set.exists():
            return self.inventarioreal_set.filter(cantidad__gt=0)[0]
        return None

    def valor_ventas(self):
        valor = self.detallefactura_set.filter(factura__valida=True).distinct().aggregate(suma=Sum('valor'))['suma']
        return round(valor, 2) if valor else 0

    def valor_ventas_fechas(self, inicio, fin):
        valor = self.detallefactura_set.filter(factura__valida=True, factura__fecha__range=(inicio, fin)).distinct().\
            aggregate(suma=Sum('valor'))['suma']
        return round(valor, 2) if valor else 0

    def valor_comision_ventas(self):
        return round(self.valor_ventas() * PORCIENTO_COMISION, 2)

    def valor_comision_ventas_fechas(self, inicio, fin):
        return round(self.valor_ventas_fechas(inicio, fin) * PORCIENTO_COMISION, 2)

    def valor_pagos_retencion(self):
        valor = self.detallefactura_set.filter(factura__valida=True,
                                               factura__pago__pagoretencion__isnull=False).distinct().\
            aggregate(suma=Sum('factura__pago__valor'))['suma']
        return round(valor, 2) if valor else 0

    def valor_pagos_retencion_fechas(self, inicio, fin):
        valor = self.detallefactura_set.filter(factura__valida=True,  factura__fecha__range=(inicio, fin),
                                               factura__pago__pagoretencion__isnull=False).distinct().\
            aggregate(suma=Sum('factura__pago__valor'))['suma']
        return round(valor, 2) if valor else 0

    def en_uso(self):
        return self.detallefactura_set.exists() or self.detalleingresoproducto_set.exists() or self.inventarioreal_set.exists()

    def cantidad_filas_puntos_descripcion_catalogo(self):
        cantidad = []
        if self.descripcion.__len__() < 180:
            lineas = int(round((180 - self.descripcion.__len__()) / 30.0, 0))
            if lineas >= 5:
                lineas = 4
            if 100 <= self.descripcion.__len__() < 130:
                lineas = 2
            if 65 < self.descripcion.__len__() < 100:
                lineas = 3
            if self.descripcion.__len__() > 130:
                lineas = 1
            if self.descripcion.__len__() > 160:
                lineas = 0
            for i in range(lineas):
                cantidad.append(1)
        return cantidad

    def tipo_nombre(self):
        if self.tipo == TIPO_PRODUCTO_PARA_VENTA:
            return "VENTA"
        elif self.tipo == TIPO_PRODUCTO_PARA_CONSUMO:
            return "CONSUMO"
        else:
            return "CONSIGNACION"

    def valor_inventario_sin_area(self):
        valor = self.inventarioreal_set.aggregate(costo=Sum('valor'))['costo']
        return round(valor, 2) if valor else 0

    def valor_inventario(self, area):
        valor = self.inventarioreal_set.filter(area=area).aggregate(costo=Sum('valor'))['costo']
        return round(valor, 2) if valor else 0

    def stock_inventario_sin_area(self):
        cantidad = self.inventarioreal_set.aggregate(cantidad=Sum('cantidad'))['cantidad']
        return round(cantidad, 4) if cantidad else 0

    def stock_inventario(self, area):
        cantidad = self.inventarioreal_set.filter(area=area).aggregate(cantidad=Sum('cantidad'))['cantidad']
        return round(cantidad, 4) if cantidad else 0

    def mi_inventario(self, area):
        if self.inventarioreal_set.filter(area=area).exists():
            return self.inventarioreal_set.filter(area=area)[0]
        return None

    def mi_inventario_costo(self, costo, area):
        return self.inventarioreal_set.filter(costo=costo, area=area)[0]

    def actualizar_inventario_ingreso(self, costo, cantidad, area):
        if not self.inventarioreal_set.filter(area=area).exists():
            inventario = InventarioReal(producto=self,
                                        costo=costo,
                                        cantidad=cantidad,
                                        valor=round(costo * cantidad, 2),
                                        area=area)
            inventario.save()
        else:
            inventario = self.inventarioreal_set.filter(area=area)[0]
            inventario.cantidad += cantidad
            inventario.valor = round(inventario.cantidad * costo, 2)
            inventario.save()

    def actualizar_inventario_salida(self, salida, area, modulo=""):
        cant = salida.cantidad
        for inv in self.inventarioreal_set.filter(cantidad__gt=0):
            if inv.cantidad < cant:
                cant -= inv.cantidad
                cant_descontar = inv.cantidad
            else:
                cant_descontar = cant
                cant -= cant_descontar
            # COSTO Y SALDO ANTES DEL MOVIMIENTO
            saldoinicialvalor = self.valor_inventario(area)
            saldoinicialcantidad = self.stock_inventario(area)
            inv.cantidad -= cant_descontar
            inv.valor = round(inv.cantidad * inv.costo, 2)
            inv.save()
            # ACTUALIZAR KARDEX
            kardex = KardexInventario(producto=self,
                                      inventario=inv,
                                      tipomovimiento=TIPO_MOVIMIENTO_SALIDA,
                                      saldoinicialvalor=saldoinicialvalor,
                                      saldoinicialcantidad=saldoinicialcantidad,
                                      cantidad=cant_descontar,
                                      costo=inv.costo,
                                      valor=round((inv.costo * cant_descontar), 2))
            kardex.save()
            if modulo == 'C':
                kardex.ddevcompra = salida
            else:
                kardex.dventa = salida
            kardex.save()

            # COSTO Y SALDO DESPUES DEL MOVIMIENTO
            saldofinalvalor = self.valor_inventario(area)
            saldofinalcantidad = self.stock_inventario(area)
            kardex.saldofinalcantidad = saldofinalcantidad
            kardex.saldofinalvalor = saldofinalvalor
            kardex.save()
            if cant <= 0:
                break

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.codigo:
            self.codigo = self.codigo.upper()
        super(Producto, self).save(force_insert, force_update, using)


class IngresoProducto(models.Model):
    proveedor = models.ForeignKey(Proveedor)
    tipodocumento = models.ForeignKey(TipoDocumento, blank=True, null=True)
    numerodocumento = models.CharField(max_length=20, blank=True, null=True)
    autorizacion = models.CharField(max_length=40, blank=True, null=True)
    fechadocumento = models.DateField()
    descripcion = models.CharField(max_length=200)
    fecha = models.DateField()
    usuario = models.ForeignKey(User, blank=True, null=True)
    valor = models.FloatField(default=0)
    valor_devolucion = models.FloatField(default=0)

    def __str__(self):
        return "{} - {} ({:%d-%m-%Y})".format(self.proveedor.nombre, self.numerodocumento, self.fecha)

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ('-fecha', '-id')

    def nombre_plantilla(self):
        return "Compra: #{0} | Doc: {1} | Prov: {2}".format(self.repr_id(), self.numerodocumento, self.proveedor.nombre)

    def total_ingreso(self):
        return self.detalleingresoproducto_set.all().aggregate(Sum('valor'))['valor__sum']

    def repr_id(self):
        return str(self.id).zfill(4)

    def cantidad_productos(self):
        return self.detalleingresoproducto_set.all().count()

    def valor_compra(self):
        valor = self.detalleingresoproducto_set.aggregate(suma=Sum('valor'))['suma']
        return valor if valor else 0

    def calcular_valor_devolucion(self):
        valor_dev = self.devolucioningresoproducto_set.aggregate(suma=Sum('valor'))['suma']
        return valor_dev if valor_dev else 0

    def valor_neto(self):
        return self.valor - self.valor_devolucion

    def cantidad_devolucion(self):
        return self.devolucioningresoproducto_set.aggregate(suma=Sum('cantidad'))['suma']


class DetalleIngresoProducto(models.Model):
    compra = models.ForeignKey(IngresoProducto)
    producto = models.ForeignKey(Producto)
    cantidad = models.FloatField(default=0)
    costo = models.FloatField(default=0)
    valor = models.FloatField(default=0)

    def __str__(self):
        return "{} - Cant: {} - Cu: ${}".format(self.producto, self.cantidad, self.costo)

    class Meta:
        verbose_name = 'Compra - Detalle'
        verbose_name_plural = 'Compra - Detalles'
        ordering = ('producto',)

    def repr_id(self):
        return str(self.id).zfill(4)

    def calcular_valor(self):
        return round(self.cantidad * self.costo, 2)


class DevolucionIngresoProducto(models.Model):
    compra = models.ForeignKey(IngresoProducto)
    detallecompra = models.ForeignKey(DetalleIngresoProducto)
    cantidad = models.FloatField(default=0)
    costo = models.FloatField(default=0)
    valor = models.FloatField(default=0)

    def __str__(self):
        return "Devolucion Compra {0}".format(self.repr_id())

    class Meta:
        verbose_name = 'Devolucion Compra'
        verbose_name_plural = 'Devoluciones Compras'
        ordering = ('compra', )

    def repr_id(self):
        return str(self.id).zfill(4)

    def calcular_valor(self):
        return round(self.cantidad * self.costo, 2)

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.valor = self.calcular_valor()
        super(DevolucionIngresoProducto, self).save(force_insert, force_update, using)


class InventarioReal(models.Model):
    producto = models.ForeignKey(Producto)
    cantidad = models.FloatField(default=0)
    costo = models.FloatField(default=0, verbose_name='Costo')
    valor = models.FloatField(default=0, verbose_name='Valor')
    area = models.ForeignKey(Area, blank=True, null=True)

    def __str__(self):
        return "{} - Cant: {} - Cu: ${}".format(self.producto, self.cantidad, self.costo)

    class Meta:
        verbose_name = 'Inventario Real'
        verbose_name_plural = 'Inventarios Reales'
        ordering = ('producto__codigo',)

    @staticmethod
    def flexbox_query(q):
        return InventarioReal.objects.filter(Q(producto__codigo__contains=q) |
                                             Q(producto__descripcion__contains=q) |
                                             Q(producto__alias__contains=q))

    def flexbox_repr(self):
        return "{} - {}".format(self.producto.codigo, self.producto.descripcion)

    def flexbox_alias(self):
        return [self.producto.codigo, self.producto.descripcion, self.producto.unidadmedida.id,
                self.producto.tipoproducto.id, str(self.producto.precio),
                self.producto.tipo]

    def esta_bajo_minimo(self):
        return self.cantidad <= self.producto.minimo

    def cantidad_vendida_fechas(self, inicio, fin):
        cantidad = self.producto.detallefactura_set.filter(factura__fecha__range=(inicio, fin)).distinct().aggregate(suma=Sum('cantidad'))['suma']
        return cantidad if cantidad else 0

    def mis_detalles_compras(self):
        return self.producto.detalleingresoproducto_set.all().order_by('compra__fecha')

    def mis_detalles_ventas(self):
        return self.producto.detallefactura_set.all().order_by('factura__fecha')


class Servicio(models.Model):
    codigo = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    unidadmedida = models.ForeignKey(UnidadMedida)
    tiposervicio = models.ForeignKey(TipoServicio)
    costo_estandar = models.FloatField(default=0)
    precio = models.FloatField(default=0)
    precio_cliente_normal = models.FloatField(default=0)
    precio_cliente_corporativo = models.FloatField(default=0)
    precio_cliente_vip = models.FloatField(default=0)
    alias = models.CharField(max_length=50, blank=True, null=True)
    orden = models.IntegerField(default=0)
    con_iva = models.BooleanField(default=True)
    favorito = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return '{} - {}'.format(self.codigo, self.descripcion)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        unique_together = ('codigo', )
        ordering = ('codigo',)

    def nombre_corto(self):
        return "{} - {}".format(self.codigo, self.descripcion)

    def nombre_factura(self):
        return "{} - {}".format(self.codigo, self.descripcion)[:70]

    def get_tipo(self):
        return "SERVICIO"

    def secuencia_codigo(self):
        return int(self.codigo.split("-")[2])

    @staticmethod
    def flexbox_query(q):
        return Servicio.objects.filter(Q(codigo__contains=q) | Q(descripcion__contains=q))

    def flexbox_repr(self):
        return "{} - {}".format(self.codigo, self.descripcion)

    def flexbox_alias(self):
        return [self.codigo, self.descripcion, self.unidadmedida.id,
                self.tiposervicio.id, str(self.precio), self.tiposervicio.nombre]

    def mi_receta(self):
        return self.receta_set.all()

    def cantidad_producto_receta(self):
        return self.receta_set.count()

    def en_uso(self):
        return self.receta_set.exists()

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.codigo:
            self.codigo = self.codigo.upper()
        super(Servicio, self).save(force_insert, force_update, using)


class Receta(models.Model):
    servicio = models.ForeignKey(Servicio)
    producto = models.ForeignKey(Producto)

    def __str__(self):
        return '{} - {}'.format(self.servicio, self.producto)

    class Meta:
        verbose_name = 'Receta'
        verbose_name_plural = 'Receta'
        unique_together = ('servicio', 'producto')
        ordering = ('servicio',)


TIPOS_PAQUETES = (
    (PAQUETE_PROMOCIONAL, 'PROMOCIONAL'),
    (PAQUETE_MULTISESION, 'MULTISESION'),
    (PAQUETE_SERVICIO, 'SERVICIO'),
)


class Paquete(models.Model):
    codigo = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.FloatField(default=0)
    precio_cliente_normal = models.FloatField(default=0)
    porciento_cliente_normal = models.FloatField(default=0)
    valor_cliente_normal = models.FloatField(default=0)
    precio_cliente_corporativo = models.FloatField(default=0)
    porciento_cliente_corporativo = models.FloatField(default=0)
    valor_cliente_corporativo = models.FloatField(default=0)
    precio_cliente_vip = models.FloatField(default=0)
    porciento_cliente_vip = models.FloatField(default=0)
    valor_cliente_vip = models.FloatField(default=0)
    alias = models.CharField(max_length=50, blank=True, null=True)
    activo = models.BooleanField(default=True)
    completo = models.BooleanField(default=False)
    tipo = models.IntegerField(choices=TIPOS_PAQUETES, default=PAQUETE_PROMOCIONAL)
    sesiones = models.IntegerField(default=1)

    def __str__(self):
        return '{} - {} ({})'.format(self.codigo, self.descripcion, self.sesiones)

    class Meta:
        verbose_name = 'Paquete'
        verbose_name_plural = 'Paquetes'
        unique_together = ('codigo', )
        ordering = ('codigo',)

    def nombre_corto(self):
        return "{} - {}".format(self.codigo, self.descripcion)

    def nombre_factura(self):
        return "{} - {}".format(self.codigo, self.descripcion)[:70]

    def get_tipo(self):
        return "PAQUETE"

    def secuencia_codigo(self):
        return int(self.codigo.split("-")[2])

    @staticmethod
    def flexbox_query(q):
        return Paquete.objects.filter(Q(codigo__contains=q) | Q(descripcion__contains=q))

    def flexbox_repr(self):
        return "{} - {}".format(self.codigo, self.descripcion)

    def flexbox_alias(self):
        return [self.codigo, self.descripcion, str(self.precio)]

    def calcular_precio_producto_referencial(self):
        valor = self.paqueteproducto_set.aggregate(suma=Sum('producto__precio'))['suma']
        return round(valor, 2) if valor else 0

    def calcular_precio_producto_cliente_normal(self):
        valor_prod = self.paqueteproducto_set.aggregate(suma=Sum('producto__precio_cliente_normal'))['suma']
        return round(valor_prod, 2) if valor_prod else 0
    
    def calcular_precio_producto_cliente_corporativo(self):
        valor_prod = self.paqueteproducto_set.aggregate(suma=Sum('producto__precio_cliente_corporativo'))['suma']
        return round(valor_prod, 2) if valor_prod else 0
    
    def calcular_precio_producto_cliente_vip(self):
        valor_prod = self.paqueteproducto_set.aggregate(suma=Sum('producto__precio_cliente_vip'))['suma']
        return round(valor_prod, 2) if valor_prod else 0
    
    def calcular_precio_servicio_referencial(self):
        valor = self.paqueteservicio_set.aggregate(suma=Sum('servicio__precio'))['suma']
        return round(valor, 2) if valor else 0

    def calcular_precio_servicio_cliente_normal(self):
        valor_prod = self.paqueteservicio_set.aggregate(suma=Sum('servicio__precio_cliente_normal'))['suma']
        return round(valor_prod, 2) if valor_prod else 0
    
    def calcular_precio_servicio_cliente_corporativo(self):
        valor_prod = self.paqueteservicio_set.aggregate(suma=Sum('servicio__precio_cliente_corporativo'))['suma']
        return round(valor_prod, 2) if valor_prod else 0
    
    def calcular_precio_servicio_cliente_vip(self):
        valor_prod = self.paqueteservicio_set.aggregate(suma=Sum('servicio__precio_cliente_vip'))['suma']
        return round(valor_prod, 2) if valor_prod else 0

    def calcular_precio_total_referencial(self):
        return self.calcular_precio_producto_referencial() + self.calcular_precio_servicio_referencial()

    def calcular_precio_total_cliente_normal(self):
        return self.calcular_precio_producto_cliente_normal() + self.calcular_precio_servicio_cliente_normal()

    def calcular_precio_total_cliente_corporativo(self):
        return self.calcular_precio_producto_cliente_corporativo() + self.calcular_precio_servicio_cliente_corporativo()

    def calcular_precio_total_cliente_vip(self):
        return self.calcular_precio_producto_cliente_vip() + self.calcular_precio_servicio_cliente_vip()

    def calcular_valores_cliente_normal(self):
        if self.porciento_cliente_normal:
            return self.precio_cliente_normal - round(self.precio_cliente_normal * self.porciento_cliente_normal / 100.0, 2)
        return self.precio_cliente_normal

    def calcular_valores_cliente_corporativo(self):
        if self.porciento_cliente_corporativo:
            return self.precio_cliente_corporativo - round(self.precio_cliente_corporativo * self.porciento_cliente_corporativo / 100.0, 2)
        return self.precio_cliente_corporativo

    def calcular_valores_cliente_vip(self):
        if self.porciento_cliente_vip:
            return self.precio_cliente_vip - round(self.precio_cliente_vip * self.porciento_cliente_vip / 100.0, 2)
        return self.precio_cliente_vip

    def mis_productos(self):
        return self.paqueteproducto_set.all()

    def cantidad_productos(self):
        return self.paqueteproducto_set.count()

    def mis_servicios(self):
        return self.paqueteservicio_set.all()

    def cantidad_servicios(self):
        return self.paqueteservicio_set.count()

    def cantidad_elementos(self):
        return self.cantidad_productos() + self.cantidad_servicios()

    def en_uso(self):
        return self.paqueteproducto_set.exists() or self.paqueteservicio_set.exists()

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.id:
            self.precio = self.calcular_precio_total_referencial()
            self.precio_cliente_normal = self.calcular_precio_total_cliente_normal()
            self.precio_cliente_corporativo = self.calcular_precio_total_cliente_corporativo()
            self.precio_cliente_vip = self.calcular_precio_total_cliente_vip()

            self.valor_cliente_normal = self.calcular_valores_cliente_normal()
            self.valor_cliente_corporativo = self.calcular_valores_cliente_corporativo()
            self.valor_cliente_vip = self.calcular_valores_cliente_vip()

            self.completo = False
            if self.cantidad_productos() or self.cantidad_servicios():
                self.completo = True
            if self.codigo:
                self.codigo = self.codigo.upper()
        super(Paquete, self).save(force_insert, force_update, using)


class PaqueteProducto(models.Model):
    paquete = models.ForeignKey(Paquete)
    producto = models.ForeignKey(Producto, blank=True, null=True)

    def __str__(self):
        return '{} ({})'.format(self.paquete, self.producto)

    class Meta:
        verbose_name = 'Paquete - Producto'
        verbose_name_plural = 'Paquete - Productos'
        unique_together = ('paquete', 'producto')
        ordering = ('paquete',)


class PaqueteServicio(models.Model):
    paquete = models.ForeignKey(Paquete)
    servicio = models.ForeignKey(Servicio, blank=True, null=True)

    def __str__(self):
        return '{} ({})'.format(self.paquete, self.servicio)

    class Meta:
        verbose_name = 'Paquete - Servicio'
        verbose_name_plural = 'Paquete - Servicios'
        unique_together = ('paquete', 'servicio')
        ordering = ('paquete',)


class SesionCaja(models.Model):
    cajero = models.ForeignKey(Cajero, blank=True, null=True)
    fecha = models.DateTimeField()
    fondo = models.FloatField(default=0)
    abierta = models.BooleanField(default=False)
    # cierre
    bill100 = models.IntegerField(null=True, blank=True, default=0)
    bill50 = models.IntegerField(null=True, blank=True, default=0)
    bill20 = models.IntegerField(null=True, blank=True, default=0)
    bill10 = models.IntegerField(null=True, blank=True, default=0)
    bill5 = models.IntegerField(null=True, blank=True, default=0)
    bill2 = models.IntegerField(null=True, blank=True, default=0)
    bill1 = models.IntegerField(null=True, blank=True, default=0)
    enmonedas = models.FloatField(default=0)
    transferencia = models.FloatField(default=0)
    deposito = models.FloatField(default=0)
    cheque = models.FloatField(default=0)
    total = models.FloatField(default=0)
    fechacierre = models.DateField(blank=True, null=True)
    horacierre = models.TimeField(blank=True, null=True)

    def __str__(self):
        return "SC: {} [{:%d-%m-%Y}] ".format(self.cajero.nombre, self.fecha)

    class Meta:
        verbose_name = "Sesion de Caja"
        verbose_name_plural = "Sesiones de Caja"
        ordering = ('-fecha', )

    @staticmethod
    def flexbox_query(q):
        if len(q) == 10 and q[2] == '-' and q[2] == '-':
            try:
                fecha = datetime(int(q[6:10]), int(q[3:5]), int(q[0:2])).date()
                return SesionCaja.objects.filter(fecha=fecha)
            except:
                pass

        return SesionCaja.objects.filter(Q(caja__nombre__contains=q) |
                                         Q(caja__usuario__first_name__contains=q) |
                                         Q(caja__usuario__last_name__contains=q) |
                                         Q(fecha__icontains=q))

    def flexbox_repr(self):
        return "SC: {} [{:%d-%m-%Y}, {:%H:%M}] ".format(self.cajero.nombre, self.fecha, self.fecha)

    def flexbox_alias(self):
        return "SC: {} [{:%d-%m-%Y}, {:%H:%M}] ".format(self.cajero.nombre, self.fecha, self.fecha)

    def valor_ventas(self):
        valor = self.factura_set.filter(valida=True).aggregate(suma=Sum('total'))['suma']
        return round(valor, 2) if valor else 0

    def valor_pagos(self):
        valor = self.factura_set.filter(valida=True).aggregate(suma=Sum('pagado'))['suma']
        return round(valor, 2) if valor else 0

    def valor_pendiente(self):
        return self.valor_ventas() - self.valor_pagos()

    def cantidad_ventas(self):
        return self.factura_set.filter(valida=True).count()

    def cantidad_facturas(self):
        return self.factura_set.filter(valida=True).count()

    def comision_ventas(self):
        return self.valor_ventas() * PORCIENTO_COMISION  # 5% comision

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if not self.bill100:
            self.bill100 = 0
        if not self.bill50:
            self.bill50 = 0
        if not self.bill20:
            self.bill20 = 0
        if not self.bill10:
            self.bill10 = 0
        if not self.bill5:
            self.bill5 = 0
        if not self.bill2:
            self.bill2 = 0
        if not self.bill1:
            self.bill1 = 0
        if not self.enmonedas:
            self.enmonedas = 0
        if not self.deposito:
            self.deposito = 0
        if not self.cheque:
            self.cheque = 0
        if not self.transferencia:
            self.transferencia = 0
        self.total = self.bill100 * 100 + self.bill50 * 50 + self.bill20 * 20 + self.bill10 * 10 + self.bill5 * 5 + \
            self.bill2 * 2 + self.bill1 * 1 + self.enmonedas + self.cheque + self.deposito + self.transferencia
        super(SesionCaja, self).save(force_insert, force_update, using=using)


class Factura(models.Model):
    sesioncaja = models.ForeignKey(SesionCaja)
    cliente = models.ForeignKey(Cliente)
    vendedor = models.ForeignKey(Vendedor, blank=True, null=True)
    cajero = models.ForeignKey(Cajero, blank=True, null=True)
    numero = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    bruto = models.FloatField(default=0)
    descuento = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)
    iva = models.FloatField(default=0)
    total = models.FloatField(default=0)
    pagado = models.FloatField(default=0)
    cancelada = models.BooleanField(default=False)
    valida = models.BooleanField(default=True)
    usuarioanula = models.CharField(max_length=20, blank=True, null=True)
    motivoanulacion = models.CharField(max_length=200, blank=True, null=True)
    notaventa = models.BooleanField(default=False)
    observaciones = models.TextField(default='', blank=True, null=True)
    valorpagado = models.FloatField(default=0)
    cambio = models.FloatField(default=0)
    valor_devolucion = models.FloatField(default=0)

    def __str__(self):
        return "{} - {} ({})".format(self.numero, self.cliente, self.total)

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ('-fecha', 'numero')

    def repr_id(self):
        return str(self.id).zfill(4)

    def saldo_pendiente(self):
        return self.total - self.pagado - self.valor_devolucion

    def esta_cancelada(self):
        return self.saldo_pendiente() == 0

    def recalcular_pagado(self):
        valor = self.pago_set.exclude(pagocheque__protestado=True).aggregate(suma=Sum('valor'))['suma']
        return round(valor, 2) if valor else 0

    def cantidad_productos(self):
        return self.detallefactura_set.all().count()

    def valor_comision(self):
        return round(self.total * PORCIENTO_COMISION, 2)

    def puede_anular(self):
        return datetime.now().date() <= (self.fecha + timedelta(days=NUMERO_DIAS_ANULAR_FACTURAS))

    def mis_detalles(self):
        return self.detallefactura_set.all()

    def tiene_pagos_asociados(self):
        return self.pago_set.exists()

    def calcular_valor_devolucion(self):
        valor_dev = self.devolucionventa_set.aggregate(suma=Sum('valor'))['suma']
        return valor_dev if valor_dev else 0

    def actualizar_bruto(self):
        valor = self.detallefactura_set.aggregate(suma=Sum('valor_bruto'))['suma']
        return round(valor, 2) if valor else 0

    def actualizar_descuento(self):
        valor = self.detallefactura_set.aggregate(suma=Sum('valor_descuento'))['suma']
        return round(valor, 2) if valor else 0

    def actualizar_subtotal(self):
        return self.actualizar_bruto() - self.actualizar_descuento()

    def mis_colaboradores(self):
        return [x.colaborador for x in self.detallefactura_set.filter(colaborador__isnull=False)]

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.pagado = self.recalcular_pagado()
        self.cancelada = self.esta_cancelada()
        super(Factura, self).save(force_insert, force_update, using)


class DetalleFactura(models.Model):
    TIPOS_VALORACIONES = (
        (0, ''),
        (VALORACION_EXCELENTE, 'EXCELENTE'),
        (VALORACION_MUYBIEN, 'MUY BIEN'),
        (VALORACION_BIEN, 'BIEN'),
        (VALORACION_REGULAR, 'REGULAR'),
        (VALORACION_MAL, 'MAL')
    )
    factura = models.ForeignKey(Factura)
    producto = models.ForeignKey(Producto, blank=True, null=True)
    servicio = models.ForeignKey(Servicio, blank=True, null=True)
    paquete = models.ForeignKey(Paquete, blank=True, null=True)
    colaborador = models.ForeignKey(Colaborador, blank=True, null=True)
    cantidad = models.FloatField(default=0)
    precio = models.FloatField(default=0)
    valor_bruto = models.FloatField(default=0)
    porciento_descuento = models.FloatField(default=0)
    valor_descuento = models.FloatField(default=0)
    valor = models.FloatField(default=0)
    recomendaciones_producto = models.TextField(blank=True, null=True)
    recomendaciones_servicio = models.TextField(blank=True, null=True)
    valoracion_producto = models.IntegerField(choices=TIPOS_VALORACIONES, default=0)
    valoracion_servicio = models.IntegerField(choices=TIPOS_VALORACIONES, default=0)

    def __str__(self):
        if self.producto:
            return "{} - {}".format(self.producto, self.cantidad)
        return "{} - {}".format(self.servicio, self.cantidad)

    class Meta:
        verbose_name = "Detalle Factura"
        verbose_name_plural = "Detalles Facturas"
        ordering = ('factura',)

    def repr_id(self):
        return str(self.id).zfill(4)

    def recalcular_valor_bruto(self):
        return round(self.cantidad * self.precio, 2)

    def recalcular_valor_descuento(self):
        return round(self.valor_bruto * self.porciento_descuento, 2)

    def recalcular_valor_neto(self):
        return round(self.valor_bruto - self.valor_descuento, 2)

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.id:
            self.valor_bruto = self.recalcular_valor_bruto()
            self.valor_descuento = self.recalcular_valor_descuento()
            self.valor = self.recalcular_valor_neto()
        super(DetalleFactura, self).save(force_insert, force_update, using)


class Sesion(models.Model):
    factura = models.ForeignKey(Factura, blank=True, null=True)
    cliente = models.ForeignKey(Cliente)
    paquete = models.ForeignKey(Paquete)
    colaborador = models.ForeignKey(Colaborador)
    fecha = models.DateField(blank=True, null=True)
    proxima_cita = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    cerrada = models.BooleanField(default=False)

    def __str__(self):
        return '{}, {} ({}) {}'.format(self.factura, self.paquete, self.cliente, self.colaborador)

    class Meta:
        verbose_name = 'Sesion'
        verbose_name_plural = 'Sesiones'
        ordering = ('paquete', 'cliente')


class DevolucionVenta(models.Model):
    venta = models.ForeignKey(Factura)
    detalleventa = models.ForeignKey(DetalleFactura)
    cantidad = models.FloatField(default=0)
    precio = models.FloatField(default=0)
    valor = models.FloatField(default=0)

    def __str__(self):
        return "Devolucion Venta {0}".format(self.repr_id())

    class Meta:
        verbose_name = 'Devolucion Venta'
        verbose_name_plural = 'Devoluciones Ventas'
        ordering = ('venta', )

    def repr_id(self):
        return str(self.id).zfill(4)

    def calcular_valor(self):
        return round(self.cantidad * self.precio, 2)

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.valor = self.calcular_valor()
        super(DevolucionVenta, self).save(force_insert, force_update, using)


class KardexInventario(models.Model):
    TIPOS_MOVIMIENTO_INVENTARIO = (
        (TIPO_MOVIMIENTO_ENTRADA, 'ENTRADA'),
        (TIPO_MOVIMIENTO_SALIDA, 'SALIDA'),
    )
    producto = models.ForeignKey(Producto, verbose_name='Producto')
    inventario = models.ForeignKey(InventarioReal, verbose_name='Inventario')
    tipomovimiento = models.IntegerField(default=1, choices=TIPOS_MOVIMIENTO_INVENTARIO, verbose_name='Tipo Movimiento')
    fecha = models.DateField(auto_now_add=True, verbose_name='Fecha')
    dcompra = models.ForeignKey(DetalleIngresoProducto, blank=True, null=True, verbose_name='Compra')
    ddevcompra = models.ForeignKey(DevolucionIngresoProducto, blank=True, null=True, verbose_name='Devolucion Compra')
    dventa = models.ForeignKey(DetalleFactura, blank=True, null=True, verbose_name='Venta')
    ddevventa = models.ForeignKey(DevolucionVenta, blank=True, null=True, verbose_name='Devolucion Venta')
    saldoinicialvalor = models.FloatField(default=0, verbose_name='Saldo Inicial Valor')
    saldoinicialcantidad = models.FloatField(default=0, verbose_name='Saldo Inicial Cantidad')
    cantidad = models.FloatField(default=0, verbose_name='Cantidad')
    costo = models.FloatField(default=0, verbose_name='Costo')
    valor = models.FloatField(default=0, verbose_name='Valor')
    saldofinalvalor = models.FloatField(default=0, verbose_name='Saldo Final Valores')
    saldofinalcantidad = models.FloatField(default=0, verbose_name='Saldo Final Cantidad')

    def __str__(self):
        return "%s - %s (%s, %s)" % (self.inventario.producto.codigo, self.cantidad, self.tipomovimiento, self.fecha)

    class Meta:
        verbose_name = 'Kardex de inventario'
        verbose_name_plural = 'Kardexs de inventario'
        ordering = ('fecha', 'id')

    def es_compra(self):
        if self.dcompra:
            return True
        if self.ddevventa:
            return True
        return False

    def es_salida(self):
        if self.dventa:
            return True
        if self.ddevcompra:
            return True
        return False


class Pago(models.Model):
    factura = models.ForeignKey(Factura)
    valor = models.FloatField(default=0)
    fecha = models.DateField()
    observaciones = models.TextField(default='')

    def __str__(self):
        return "{} ({}, $ {})".format(self.repr_id(), self.valor, self.factura.numero)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ('factura', '-fecha')

    def repr_id(self):
        return str(self.id).zfill(4)

    def tipo(self):
        if self.pagoefectivo_set.exists():
            return 'EFECTIVO'
        elif self.pagocheque_set.exists():
            return 'CHEQUE'
        elif self.pagodeposito_set.exists():
            return 'DEPOSITO'
        elif self.pagotransferencia_set.exists():
            return 'TRANSFERENCIA'
        elif self.pagotarjeta_set.exists():
            return 'TARJETA'
        elif self.pagoretencion_set.exists():
            return 'RETENCION'
        else:
            return ''

    def es_efectivo(self):
        return self.pagoefectivo_set.exists()

    def pago_efectivo(self):
        if self.es_efectivo():
            return self.pagoefectivo_set.all()[0]
        return None

    def es_cheque(self):
        return self.pagocheque_set.exists()

    def pago_cheque(self):
        if self.es_cheque():
            return self.pagocheque_set.all()[0]
        return None

    def es_deposito(self):
        return self.pagodeposito_set.exists()

    def pago_deposito(self):
        if self.es_deposito():
            return self.pagodeposito_set.all()[0]
        return None

    def es_transferencia(self):
        return self.pagotransferencia_set.exists()

    def pago_transferencia(self):
        if self.es_transferencia():
            return self.pagotransferencia_set.all()[0]
        return None

    def es_tarjeta(self):
        return self.pagotarjeta_set.exists()

    def pago_tarjeta(self):
        if self.es_tarjeta():
            return self.pagotarjeta_set.all()[0]
        return None

    def es_retencion(self):
        return self.pagoretencion_set.exists()

    def pago_retencion(self):
        if self.es_retencion():
            return self.pagoretencion_set.all()[0]
        return None


class PagoEfectivo(models.Model):
    pago = models.ForeignKey(Pago)

    def __str__(self):
        return "Pago Efectivo: {}".format(self.pago)

    class Meta:
        verbose_name = "Pago - Efectivo"
        verbose_name_plural = "Pagos - Efectivo"
        ordering = ('pago', )


class PagoCheque(models.Model):
    pago = models.ForeignKey(Pago)
    numero = models.CharField(max_length=50, blank=True, null=True)
    banco = models.ForeignKey(Banco, blank=True, null=True)
    emite = models.CharField(max_length=100, blank=True, null=True)
    postfechado = models.BooleanField(default=False)
    depositado = models.BooleanField(default=False)
    fechadepositado = models.DateField(blank=True, null=True)
    protestado = models.BooleanField(default=False)

    def __str__(self):
        return "Pago Cheque: {}".format(self.pago)

    class Meta:
        verbose_name = "Pago - Cheque"
        verbose_name_plural = "Pagos - Cheque"
        unique_together = ('numero', )
        ordering = ('pago',)

    def cheque_protestado(self):
        if self.protestado and self.chequeprotestado_set.all().exists():
            return self.chequeprotestado_set.all()[0]
        return None


class PagoDeposito(models.Model):
    pago = models.ForeignKey(Pago)
    numero = models.CharField(max_length=100)
    efectuadopor = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "Pago Deposito: {}".format(self.pago)

    class Meta:
        verbose_name = "Pago - Deposito"
        verbose_name_plural = "Pagos - Depositos"
        unique_together = ('numero', )
        ordering = ('pago',)


class PagoTransferencia(models.Model):
    pago = models.ForeignKey(Pago)
    numero = models.CharField(max_length=100)
    efectuadopor = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "Pago Transferencia: {}".format(self.pago)

    class Meta:
        verbose_name = "Pago - Transferencia"
        verbose_name_plural = "Pagos - Transferencia"
        unique_together = ('numero', )
        ordering = ('pago',)


class PagoTarjeta(models.Model):
    pago = models.ForeignKey(Pago)
    tipotarjeta = models.ForeignKey(TipoTarjetaBanco, blank=True, null=True)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    lote = models.CharField(max_length=100, blank=True, null=True)
    banco = models.ForeignKey(Banco, blank=True, null=True)
    poseedor = models.CharField(max_length=100, blank=True, null=True)
    procesadorpago = models.ForeignKey(ProcesadorPagoTarjeta, blank=True, null=True)

    def __str__(self):
        return "Pago Tarjeta: {}".format(self.pago)

    class Meta:
        verbose_name = "Pago - Tarjeta"
        verbose_name_plural = "Pagos - Tarjetas"
        unique_together = ('referencia', 'banco')
        ordering = ('pago',)


class PagoRetencion(models.Model):
    pago = models.ForeignKey(Pago)
    numero = models.CharField(max_length=50)

    def __str__(self):
        return "Pago Retencion: {}".format(self.pago)

    class Meta:
        verbose_name = "Pago - Retencion"
        verbose_name_plural = "Pagos - Retencion"
        unique_together = ('numero', )
        ordering = ('pago',)


class ChequeProtestado(models.Model):
    cheque = models.ForeignKey(PagoCheque, verbose_name='Cheque')
    motivo = models.CharField(default='', max_length=300, verbose_name='Motivo')
    fecha = models.DateField(verbose_name='Fecha')

    def __str__(self):
        return 'Cheque protestado No. {} - {:%d-%m-%Y}'.format(self.cheque.numero, self.fecha)

    class Meta:
        verbose_name = "Cheque protestado"
        verbose_name_plural = "Cheques protestados"
        unique_together = ('cheque', )
        ordering = ('fecha',)


# Models para ordenes de servicios (Colaboradores)
class OrdenServicio(models.Model):
    cliente = models.ForeignKey(Cliente)
    colaborador = models.ForeignKey(Colaborador, blank=True, null=True)
    fecha = models.DateField(auto_now_add=True)
    subtotal = models.FloatField(default=0)
    iva = models.FloatField(default=0)
    total = models.FloatField(default=0)
    factura_asignada = models.ForeignKey(Factura, blank=True, null=True)
    fecha_asignada = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{} - {} ({}, {})".format(self.cliente, self.total, self.colaborador, self.fecha)

    class Meta:
        verbose_name = "Orden de Servicio"
        verbose_name_plural = "Ordenes de Servicios"
        ordering = ('-fecha', '-id', 'cliente')

    def repr_id(self):
        return str(self.id).zfill(4)

    def cantidad_productos(self):
        return self.ordenserviciodetalle_set.filter(producto__isnull=False).count()

    def cantidad_servicios(self):
        return self.ordenserviciodetalle_set.filter(servicio__isnull=False).count()

    def en_uso(self):
        return self.factura_asignada


class OrdenServicioDetalle(models.Model):
    orden = models.ForeignKey(OrdenServicio)
    servicio = models.ForeignKey(Servicio, blank=True, null=True)
    producto = models.ForeignKey(Producto, blank=True, null=True)
    cantidad = models.FloatField(default=0)
    precio = models.FloatField(default=0)
    valor = models.FloatField(default=0)

    def __str__(self):
        return "{} - {}".format(self.producto, self.cantidad)

    class Meta:
        verbose_name = "Orden Servicio - Detalles"
        verbose_name_plural = "Ordenes Servicios - Detalles"
        ordering = ('orden',)


class ServicioFuturo(models.Model):
    orden = models.ForeignKey(OrdenServicio, blank=True, null=True)
    cliente = models.ForeignKey(Cliente)
    servicio = models.ForeignKey(Servicio)
    fecha = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return "{} - {} (Orden: {})".format(self.cliente, self.servicio, self.orden.id)

    class Meta:
        verbose_name = "Servicio futuro"
        verbose_name_plural = "Servicios futuros"
        ordering = ('fecha', 'cliente')


class SolicitudCompra(models.Model):
    ESTADOS_SOLICITUD = (
        (ESTADO_SOLICITUD_PENDIENTE, 'Pendiente'),
        (ESTADO_SOLICITUD_APROBADA, 'Aprobada'),
        (ESTADO_SOLICITUD_DENEGADA, 'Denegada'),
        (ESTADO_SOLICITUD_ASIGNADA, 'Asignada'),
    )
    cliente = models.ForeignKey(Cliente)
    vendedor = models.ForeignKey(Vendedor, blank=True, null=True)
    fecha = models.DateField()
    subtotal = models.FloatField(default=0)
    iva = models.FloatField(default=0)
    total = models.FloatField(default=0)
    estado = models.IntegerField(choices=ESTADOS_SOLICITUD, default=ESTADO_SOLICITUD_PENDIENTE)
    factura_asignada = models.ForeignKey(Factura, blank=True, null=True)
    fecha_asignada = models.DateField(blank=True, null=True)
    observaciones = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return "{} - {} ({})".format(self.cliente, self.fecha, self.total)

    class Meta:
        verbose_name = "Solicitud de compra"
        verbose_name_plural = "Solicitudes de compras"
        ordering = ('estado', '-fecha')

    def repr_id(self):
        return str(self.id).zfill(4)

    def cantidad_productos(self):
        return self.detallesolicitudcompra_set.all().count()

    def cantidad_facturas_asignadas(self):
        return Factura.objects.filter(solicitudcompra=self).distinct().count()

    def es_vendedor(self):
        return self.cliente and self.vendedor

    def es_cliente(self):
        return self.cliente and not self.vendedor


class DetalleSolicitudCompra(models.Model):
    solicitud = models.ForeignKey(SolicitudCompra)
    producto = models.ForeignKey(Producto)
    cantidad = models.FloatField(default=0)
    precio = models.FloatField(default=0)
    valor = models.FloatField(default=0)

    def __str__(self):
        return "{} - {}".format(self.producto, self.cantidad)

    class Meta:
        verbose_name = "Solicitud de compra - Detalle"
        verbose_name_plural = "Solicitudes de compras - Detalles"
        ordering = ('solicitud',)


# Models para HISTORIALES de cambio de precios y costos de productos
class HistorialPrecioProducto(models.Model):
    producto = models.ForeignKey(Producto)
    precio = models.FloatField(default=0)
    precio_cliente_normal = models.FloatField(default=0)
    precio_cliente_corporativo = models.FloatField(default=0)
    precio_cliente_vip = models.FloatField(default=0)
    fecha = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, blank=True, null=True)
    modulo = models.CharField(max_length=1, blank=True, null=True)
    accion = models.CharField(default=ACCION_ADICIONAR, max_length=1)

    def __str__(self):
        return "{} - {} ({})".format(self.producto, self.fecha, self.precio)

    class Meta:
        verbose_name = "Historial de precio - Producto"
        verbose_name_plural = "Historial de precios - Productos"
        ordering = ('-fecha', )

    def repr_id(self):
        return str(self.id).zfill(4)


class HistorialPrecioServicio(models.Model):
    servicio = models.ForeignKey(Servicio)
    precio = models.FloatField(default=0)
    precio_cliente_normal = models.FloatField(default=0)
    precio_cliente_corporativo = models.FloatField(default=0)
    precio_cliente_vip = models.FloatField(default=0)
    fecha = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, blank=True, null=True)
    modulo = models.CharField(max_length=1, blank=True, null=True)
    accion = models.CharField(default=ACCION_ADICIONAR, max_length=1)

    def __str__(self):
        return "{} ({})".format(self.servicio.nombre_corto(), self.fecha)

    class Meta:
        verbose_name = "Historial de precio - Servicio"
        verbose_name_plural = "Historial de precios - Servicios"
        ordering = ('-fecha', )

    def repr_id(self):
        return str(self.id).zfill(4)


class HistorialCifProducto(models.Model):
    producto = models.ForeignKey(Producto)
    compra = models.ForeignKey(IngresoProducto)
    cif = models.FloatField(default=0)
    fecha = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, blank=True, null=True)

    def __str__(self):
        return "{} - {} ({})".format(self.producto, self.fecha, self.cif)

    class Meta:
        verbose_name = "Historial de CIF"
        verbose_name_plural = "Historial de CIF"
        ordering = ('-fecha', )

    def repr_id(self):
        return str(self.id).zfill(4)


class Archivo(models.Model):
    nombre = models.CharField(default='', max_length=300, verbose_name='Nombre')
    fecha = models.DateTimeField(verbose_name='Fecha')
    archivo = models.FileField(upload_to='archivos/%Y/%m/%d', verbose_name='Archivo')

    def __str__(self):
        return '%s' % self.nombre

    class Meta:
        verbose_name = 'Archivo'
        verbose_name_plural = "Archivos"
        db_table = "archivos"
        unique_together = ('fecha', 'nombre',)

    def nombre_archivo(self):
        return os.path.split(str(self.archivo.name))[1]

    def tipo_archivo(self):
        a = self.nombre_archivo()
        n = a[a.rindex(".") + 1:]
        if n == 'pdf' or n == 'doc' or n == 'docx':
            return n
        return 'other'

    def download_link(self):
        return self.archivo.url

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper().strip()
        super(Archivo, self).save(*args, **kwargs)


# Auditorias y Control de conexiones en requests
class AudiUsuarioTabla(models.Model):
    TIPOS_ACCIONES = (
        ('A', 'A'),   # Adicion
        ('M', 'M'),   # Modificacion
        ('E', 'E')    # Eliminacion
    )
    usuario = models.ForeignKey(User, verbose_name='Usuario')
    tabla = models.CharField(max_length=100, verbose_name='Tabla')
    registroid = models.IntegerField(verbose_name='Registro Id')
    accion = models.CharField(choices=TIPOS_ACCIONES, max_length=2, verbose_name='Accion')
    fecha = models.DateField(verbose_name='Fecha')
    hora = models.TimeField(verbose_name='Hora')
    estacion = models.CharField(max_length=100, verbose_name='Estacion')

    def __str__(self):
        return "{} - {} [{}]".format(self.usuario.username, self.tabla, self.accion)

    class Meta:
        verbose_name = 'Auditoria Usuario '
        verbose_name_plural = 'Auditorias Usuarios'
        ordering = ('-fecha', 'hora')
