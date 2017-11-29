from django.contrib import admin
from inv.models import *


# ADMINS MTTO

class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'latitud', 'longitud')
    ordering = ('nombre', )
    search_fields = ('nombre',)

admin.site.register(Provincia, ProvinciaAdmin)


class CantonAdmin(admin.ModelAdmin):
    list_display = ('provincia', 'nombre', 'latitud', 'longitud')
    ordering = ('provincia', )
    search_fields = ('provincia__nombre', 'nombre')

admin.site.register(Canton, CantonAdmin)


class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'codigo', 'email', 'usuario')
    ordering = ('cedula', 'codigo')
    search_fields = ('cedula', 'nombre', 'codigo')

admin.site.register(Colaborador, ColaboradorAdmin)


class HistorialPrecioProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'precio', 'precio_cliente_normal', 'precio_cliente_corporativo', 'precio_cliente_vip',
                    'fecha', 'usuario', 'modulo', 'accion')
    ordering = ('-fecha', 'producto')
    search_fields = ('producto__codigo', 'producto__descripcion', 'usuario')
    list_filter = ('modulo', 'accion', 'producto__tipo')

admin.site.register(HistorialPrecioProducto, HistorialPrecioProductoAdmin)


class HistorialPrecioServicioAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'precio', 'precio_cliente_normal', 'precio_cliente_corporativo', 'precio_cliente_vip',
                    'fecha', 'usuario', 'modulo', 'accion')
    ordering = ('-fecha', 'servicio')
    search_fields = ('servicio__codigo', 'servicio__descripcion', 'usuario')
    list_filter = ('modulo', 'accion')

admin.site.register(HistorialPrecioServicio, HistorialPrecioServicioAdmin)


admin.site.register(Empresa)
admin.site.register(ParametrosEmpresa)
admin.site.register(TipoIdentificacion)
admin.site.register(TipoCabello)
admin.site.register(TipoPiel)
admin.site.register(Proveedor)
admin.site.register(TipoServicio)
admin.site.register(UnidadMedida)
admin.site.register(TipoDocumento)
admin.site.register(Vendedor)
admin.site.register(Cliente)
admin.site.register(Cajero)
admin.site.register(HistorialCifProducto)
admin.site.register(FormaDePago)
admin.site.register(Banco)
admin.site.register(TipoTarjetaBanco)
admin.site.register(ProcesadorPagoTarjeta)
admin.site.register(Area)
admin.site.register(AudiUsuarioTabla)

# END ADMIN MTTO


# ADMIN APP
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'unidadmedida', 'tipoproducto', 'orden', 'precio', 'activo', 'favorito')
    ordering = ('tipoproducto__orden', 'orden')
    search_fields = ('codigo', 'codigobarra', 'descripcion', 'tipoproducto__nombre', 'alias')
    list_filter = ('activo', 'tipoproducto__nombre')


admin.site.register(Producto, ProductoAdmin)


class ServicioAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'unidadmedida', 'tiposervicio', 'orden', 'precio', 'activo', 'favorito')
    ordering = ('tiposervicio__orden', 'orden')
    search_fields = ('codigo', 'descripcion', 'tiposervicio__nombre', 'alias')
    list_filter = ('activo', 'tiposervicio__nombre')


admin.site.register(Servicio, ServicioAdmin)


class TipoProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'orden')
    ordering = ('codigo', 'orden')
    search_fields = ('nombre', )
    list_filter = ('codigo', )


admin.site.register(TipoProducto, TipoProductoAdmin)


class IngresoProductoAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'tipodocumento', 'numerodocumento', 'fechadocumento', 'autorizacion', 'descripcion',
                    'fecha')
    ordering = ('proveedor__nombre', 'tipodocumento__nombre', 'fechadocumento', 'descripcion')
    search_fields = ('proveedor__nombre', 'tipodocumento__nombre', 'fechadocumento', 'descripcion')
    list_filter = ('proveedor', 'tipodocumento')


admin.site.register(IngresoProducto, IngresoProductoAdmin)


class DetalleIngresoProductoAdmin(admin.ModelAdmin):
    list_display = ('compra', 'producto', 'cantidad', 'costo', 'valor')
    ordering = ('producto__codigo', 'producto__alias')
    search_fields = ('producto__nombre', 'producto__codigo')

admin.site.register(DetalleIngresoProducto, DetalleIngresoProductoAdmin)


class InventarioRealAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad', 'costo', 'valor')
    ordering = ('producto__codigo', 'producto__alias')
    search_fields = ('producto__nombre', 'producto__codigo')


admin.site.register(InventarioReal, InventarioRealAdmin)


class SesionCajaAdmin(admin.ModelAdmin):
    list_display = ('cajero', 'fecha', 'fondo', 'abierta', 'total', 'bill100', 'bill50', 'bill20', 'bill10',
                    'bill5', 'bill2', 'bill1', 'enmonedas', 'deposito', 'fechacierre')
    ordering = ('-fecha', )
    search_fields = ('cajero__nombre', 'cajero__usuario__username')


admin.site.register(SesionCaja, SesionCajaAdmin)


class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha_vencimiento', 'cliente', 'cajero', 'subtotal', 'iva', 'total',
                    'fecha', 'cancelada', 'valida')
    ordering = ('fecha_vencimiento', 'numero')
    search_fields = ('numero', 'cliente__nombre')
    list_filter = ('valida', 'cajero', 'cancelada')


admin.site.register(Factura, FacturaAdmin)


class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = ('factura', 'producto', 'cantidad', 'precio', 'valor')
    ordering = ('factura', )
    search_fields = ('factura__numero', 'producto__codigo', 'producto__descripcion')


admin.site.register(DetalleFactura, DetalleFacturaAdmin)


class PagoAdmin(admin.ModelAdmin):
    list_display = ('factura', 'valor', 'fecha')
    ordering = ('-fecha', )
    search_fields = ('factura__numero',)

admin.site.register(Pago, PagoAdmin)


admin.site.register(PagoEfectivo)
admin.site.register(PagoRetencion)


class PagoChequeAdmin(admin.ModelAdmin):
    list_display = ('pago', 'numero', 'banco', 'emite', 'postfechado', 'depositado')
    search_fields = ('pago__factura__numero', 'numero', 'emite')
    list_filter = ('postfechado', 'banco', 'depositado')

admin.site.register(PagoCheque, PagoChequeAdmin)


class PagoDepositoAdmin(admin.ModelAdmin):
    list_display = ('pago', 'numero', 'efectuadopor')
    search_fields = ('pago__factura__numero', 'numero', 'efectuadopor')

admin.site.register(PagoDeposito, PagoDepositoAdmin)


class PagoTransferenciaAdmin(admin.ModelAdmin):
    list_display = ('pago', 'numero', 'efectuadopor')
    search_fields = ('pago__factura__numero', 'numero', 'efectuadopor')

admin.site.register(PagoTransferencia, PagoTransferenciaAdmin)


class PagoTarjetaAdmin(admin.ModelAdmin):
    list_display = ('pago', 'banco', 'tipotarjeta', 'referencia', 'lote', 'poseedor', 'procesadorpago')
    search_fields = ('pago__factura__numero', 'referencia', 'lote', 'poseedor')
    list_filter = ('banco', 'procesadorpago', 'tipotarjeta')

admin.site.register(PagoTarjeta, PagoTarjetaAdmin)


class OrdenServicioAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'colaborador', 'fecha', 'subtotal', 'iva', 'total', 'factura_asignada', 'fecha_asignada')
    search_fields = ('cliente__nombre', 'cliente__razon_social', 'colaborador__nombre', 'colaborador__cedula')


admin.site.register(OrdenServicio, OrdenServicioAdmin)


class OrdenServicioDetalleAdmin(admin.ModelAdmin):
    list_display = ('orden', 'servicio', 'producto', 'cantidad', 'precio', 'valor')
    search_fields = ('producto__codigo', 'producto__descripcion', 'servicio__codigo', 'servicio__descripcion')


admin.site.register(OrdenServicioDetalle, OrdenServicioDetalleAdmin)


class ServicioFuturoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'servicio')
    search_fields = ('cliente__nombre', 'servicio__codigo', 'servicio__descripcion')


admin.site.register(ServicioFuturo, ServicioFuturoAdmin)

# END ADMIN APP
