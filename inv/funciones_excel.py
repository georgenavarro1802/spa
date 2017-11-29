import io

import xlsxwriter
from datetime import datetime
from django.utils.translation import ugettext


# Ventas - Resumen (solo cabeceras)
def WriteToExcel_Ventas_Resumen(datos, search=None):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    # Here we will adding the code to add data
    worksheet_s = workbook.add_worksheet("Ventas")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    subtitle = workbook.add_format({
        'bold': True,
        'font_size': 11,
        'align': 'center',
        'valign': 'top'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'bold': True,
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1
    })

    if search:
        title_text = "{0} {1}".format(ugettext("Listado de Ventas. Filtro aplicado: "), search)
    else:
        title_text = "{0}".format(ugettext("Listado de Ventas"))
    worksheet_s.merge_range('B2:H2', title_text, title)

    fecha_text = "{0}".format(datetime.now().strftime('%A, %d-%m-%Y / %H:%I'))
    worksheet_s.merge_range('K2:M2', fecha_text, subtitle)

    # Colums Headers
    worksheet_s.write(4, 0, ugettext("No."), header)
    worksheet_s.write(4, 1, ugettext("Código"), header)
    worksheet_s.write(4, 2, ugettext("Fecha"), header)
    worksheet_s.write(4, 3, ugettext("No. Doc."), header)
    worksheet_s.write(4, 4, ugettext("Cliente"), header)
    worksheet_s.write(4, 5, ugettext("Subtotal"), header)
    worksheet_s.write(4, 6, ugettext("IVA"), header)
    worksheet_s.write(4, 7, ugettext("Total"), header)
    worksheet_s.write(4, 8, ugettext("Pagado"), header)
    worksheet_s.write(4, 9, ugettext("Pendiente"), header)
    worksheet_s.write(4, 10, ugettext("Items"), header)
    worksheet_s.write(4, 11, ugettext("Vendedor"), header)
    worksheet_s.write(4, 12, ugettext("Estado"), header)

    # Inicialization columns size for future width
    fecha_col_width = 15
    numerodocumento_col_width = 15
    cliente_col_width = 30
    valores_col_width = 15
    vendedor_col_width = 20
    estado_col_width = 20

    # Columns Content
    for idx, data in enumerate(datos):
        row = 5 + idx
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write_string(row, 1, data.repr_id(), cell)
        worksheet_s.write(row, 2, data.fecha.strftime('%d-%m-%Y'), cell_center)
        worksheet_s.write_string(row, 3, data.numero, cell)
        worksheet_s.write_string(row, 4, data.cliente.nombre if data.cliente else "", cell)
        worksheet_s.write_number(row, 5, data.subtotal, cell)
        worksheet_s.write_number(row, 6, data.iva, cell)
        worksheet_s.write_number(row, 7, data.total, cell)
        worksheet_s.write_number(row, 8, data.pagado, cell)
        worksheet_s.write_number(row, 9, data.saldo_pendiente(), cell)
        worksheet_s.write_number(row, 10, data.cantidad_productos(), cell_center)
        worksheet_s.write_string(row, 11, data.vendedor.usuario.username if data.vendedor else "", cell_center)
        worksheet_s.write_string(row, 12, data.mi_estado(), cell)

        # Set cell elements width by field length
        if len(data.numero) > numerodocumento_col_width:
            numerodocumento_col_width = len(data.numero)
        if data.cliente and len(data.cliente.nombre) > cliente_col_width:
            cliente_col_width = len(data.cliente.nombre)
        if len(data.mi_estado()) > estado_col_width:
            estado_col_width = len(data.mi_estado())

    # Resize columns data
    worksheet_s.set_column('C:C', fecha_col_width)
    worksheet_s.set_column('D:D', numerodocumento_col_width)
    worksheet_s.set_column('E:E', cliente_col_width)
    worksheet_s.set_column('F:F', valores_col_width)
    worksheet_s.set_column('G:G', valores_col_width)
    worksheet_s.set_column('H:H', valores_col_width)
    worksheet_s.set_column('I:I', valores_col_width)
    worksheet_s.set_column('J:J', valores_col_width)
    worksheet_s.set_column('L:L', vendedor_col_width)
    worksheet_s.set_column('M:M', estado_col_width)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data


# Ventas - Detallado (incluye el detalle de la venta)
def WriteToExcel_Ventas_Detallado(venta):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    # Here we will adding the code to add data
    worksheet_s = workbook.add_worksheet("Detalles de venta")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    subtitle = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'center',
        'valign': 'top'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'bold': True,
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1
    })

    title_text = "{0} {1}".format(ugettext("Detalle de la Venta: "), venta.repr_id())
    subtitle_text = "{0} {1} {2} {3}".format(ugettext("Cliente: "), venta.cliente.nombre, ugettext("Documento: "), venta.numero)
    worksheet_s.merge_range('B2:C2', title_text, title)
    worksheet_s.merge_range('B3:C3', subtitle_text, subtitle)

    fecha_text = "{0}".format(datetime.now().strftime('%A, %d-%m-%Y / %H:%I'))
    worksheet_s.merge_range('D2:F2', fecha_text, subtitle)

    # Colums Headers
    worksheet_s.write(4, 0, ugettext("No."), header)
    worksheet_s.write(4, 1, ugettext("Código"), header)
    worksheet_s.write(4, 2, ugettext("Descripción"), header)
    worksheet_s.write(4, 3, ugettext("Cantidad"), header)
    worksheet_s.write(4, 4, ugettext("Precio"), header)
    worksheet_s.write(4, 5, ugettext("Valor"), header)

    # Inicialization columns size for future width
    codigo_col_width = 25
    descripcion_col_width = 75
    valores_col_width = 10

    datos = venta.detalles.all()
    # Columns Content
    for idx, data in enumerate(datos):
        row = 5 + idx
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write_string(row, 1, data.producto.codigo, cell)
        worksheet_s.write_string(row, 2, data.producto.descripcion, cell)
        worksheet_s.write_number(row, 3, data.cantidad, cell)
        worksheet_s.write_number(row, 4, data.precio, cell)
        worksheet_s.write_number(row, 5, data.valor, cell)

        # Set cell elements width by field length
        if len(data.producto.codigo) > codigo_col_width:
            codigo_col_width = len(data.producto.codigo)
        if len(data.producto.descripcion) > descripcion_col_width:
            descripcion_col_width = len(data.producto.descripcion)

    # Resize columns data
    worksheet_s.set_column('B:B', codigo_col_width)
    worksheet_s.set_column('C:C', descripcion_col_width)
    worksheet_s.set_column('D:D', valores_col_width)
    worksheet_s.set_column('E:E', valores_col_width)
    worksheet_s.set_column('F:F', valores_col_width)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data


# Compras - Resumen (solo cabeceras)
def WriteToExcel_Compras_Resumen(datos, search=None):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    # Here we will adding the code to add data
    worksheet_s = workbook.add_worksheet("Compras")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    subtitle = workbook.add_format({
        'bold': True,
        'font_size': 11,
        'align': 'center',
        'valign': 'top'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'bold': True,
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1
    })

    if search:
        title_text = "{0} {1}".format(ugettext("Listado de Compras. Filtro aplicado: "), search)
    else:
        title_text = "{0}".format(ugettext("Listado de Compras"))
    worksheet_s.merge_range('B2:G2', title_text, title)

    fecha_text = "{0}".format(datetime.now().strftime('%A, %d-%m-%Y / %H:%I'))
    worksheet_s.merge_range('I2:K2', fecha_text, subtitle)

    # Colums Headers
    worksheet_s.write(4, 0, ugettext("No."), header)
    worksheet_s.write(4, 1, ugettext("Código"), header)
    worksheet_s.write(4, 2, ugettext("Fecha"), header)
    worksheet_s.write(4, 3, ugettext("Tipo Doc."), header)
    worksheet_s.write(4, 4, ugettext("No. Doc."), header)
    worksheet_s.write(4, 5, ugettext("Proveedor"), header)
    worksheet_s.write(4, 6, ugettext("Fecha Doc."), header)
    worksheet_s.write(4, 7, ugettext("Valor FOB"), header)
    worksheet_s.write(4, 8, ugettext("Valor CIF"), header)
    worksheet_s.write(4, 9, ugettext("Descripción"), header)
    worksheet_s.write(4, 10, ugettext("Items"), header)

    # Inicialization columns size for future width
    fechas_col_width = 15
    tipodocumento_col_width = 20
    numerodocumento_col_width = 30
    proveedor_col_width = 30
    valores_col_width = 15
    descripcion_col_width = 50

    # Columns Content
    for idx, data in enumerate(datos):
        row = 5 + idx
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write_string(row, 1, data.repr_id(), cell)
        worksheet_s.write(row, 2, data.fecha.strftime('%d-%m-%Y'), cell_center)
        worksheet_s.write_string(row, 3, data.tipodocumento.nombre if data.tipodocumento else "", cell)
        worksheet_s.write_string(row, 4, data.numerodocumento, cell)
        worksheet_s.write_string(row, 5, data.proveedor.nombre if data.proveedor else "", cell)
        worksheet_s.write(row, 6, data.fechadocumento.strftime('%d-%m-%Y'), cell_center)
        worksheet_s.write_number(row, 7, data.valorfob, cell)
        worksheet_s.write_number(row, 8, data.valor, cell)
        worksheet_s.write_string(row, 9, data.descripcion, cell)
        worksheet_s.write_number(row, 10, data.cantidad_productos(), cell_center)

        # Set cell elements width by field length
        if data.tipodocumento and len(data.tipodocumento.nombre) > tipodocumento_col_width:
            tipodocumento_col_width = len(data.tipodocumento.nombre)
        if len(data.numerodocumento) > numerodocumento_col_width:
            numerodocumento_col_width = len(data.numerodocumento)
        if data.proveedor and len(data.proveedor.nombre) > proveedor_col_width:
            proveedor_col_width = len(data.proveedor.nombre)
        if len(data.descripcion) > descripcion_col_width:
            descripcion_col_width = len(data.descripcion)

    # Resize columns data
    worksheet_s.set_column('C:C', fechas_col_width)
    worksheet_s.set_column('D:D', tipodocumento_col_width)
    worksheet_s.set_column('E:E', numerodocumento_col_width)
    worksheet_s.set_column('F:F', proveedor_col_width)
    worksheet_s.set_column('G:G', fechas_col_width)
    worksheet_s.set_column('H:H', valores_col_width)
    worksheet_s.set_column('I:I', valores_col_width)
    worksheet_s.set_column('J:J', descripcion_col_width)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data


# Compras - Detallado (incluye el detalle de la compra)
def WriteToExcel_Compras_Detallado(compra):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    # Here we will adding the code to add data
    worksheet_s = workbook.add_worksheet("Detalles de compra")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    subtitle = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'center',
        'valign': 'top'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'bold': True,
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1
    })

    title_text = "{0} {1}".format(ugettext("Detalle de la Compra: "), compra.repr_id())
    subtitle_text = "{0} {1} {2} {3}".format(ugettext("Proveedor: "), 
                                              compra.proveedor.nombre, 
                                              ugettext("Documento: "), 
                                              compra.numerodocumento)
    worksheet_s.merge_range('B2:G2', title_text, title)
    worksheet_s.merge_range('B3:G3', subtitle_text, subtitle)

    fecha_text = "{0}".format(datetime.now().strftime('%A, %d-%m-%Y / %H:%I'))
    worksheet_s.merge_range('H2:J2', fecha_text, subtitle)

    # Colums Headers
    worksheet_s.write(4, 0, ugettext("No."), header)
    worksheet_s.write(4, 1, ugettext("Código"), header)
    worksheet_s.write(4, 2, ugettext("Descripción"), header)
    worksheet_s.write(4, 3, ugettext("Cantidad"), header)
    worksheet_s.write(4, 4, ugettext("Costo FOB"), header)
    worksheet_s.write(4, 5, ugettext("Costo CIF"), header)
    worksheet_s.write(4, 6, ugettext("% CIF/FOB"), header)
    worksheet_s.write(4, 7, ugettext("% PREC/CIF"), header)
    worksheet_s.write(4, 8, ugettext("% Valor FOB"), header)
    worksheet_s.write(4, 9, ugettext("% Valor CIF"), header)

    # Inicialization columns size for future width
    codigo_col_width = 25
    descripcion_col_width = 75
    valores_col_width = 10

    datos = compra.productos.all()
    # Columns Content
    for idx, data in enumerate(datos):
        row = 5 + idx
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write_string(row, 1, data.producto.codigo, cell)
        worksheet_s.write_string(row, 2, data.producto.descripcion, cell)
        worksheet_s.write_number(row, 3, data.cantidad, cell)
        worksheet_s.write_number(row, 4, data.costofob, cell)
        worksheet_s.write_number(row, 5, data.costo, cell)
        worksheet_s.write_number(row, 6, data.porciento_cif_fob, cell)
        worksheet_s.write_number(row, 7, data.porciento_precio_cif, cell)
        worksheet_s.write_number(row, 8, data.valorfob, cell)
        worksheet_s.write_number(row, 9, data.valor, cell)

        # Set cell elements width by field length
        if len(data.producto.codigo) > codigo_col_width:
            codigo_col_width = len(data.producto.codigo)
        if len(data.producto.descripcion) > descripcion_col_width:
            descripcion_col_width = len(data.producto.descripcion)

    # Resize columns data
    worksheet_s.set_column('B:B', codigo_col_width)
    worksheet_s.set_column('C:C', descripcion_col_width)
    worksheet_s.set_column('D:D', valores_col_width)
    worksheet_s.set_column('E:E', valores_col_width)
    worksheet_s.set_column('F:F', valores_col_width)
    worksheet_s.set_column('G:G', valores_col_width)
    worksheet_s.set_column('H:H', valores_col_width)
    worksheet_s.set_column('I:I', valores_col_width)
    worksheet_s.set_column('J:J', valores_col_width)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data


# Vendedores - Facturas pendientes de cobrar
def WriteToExcel_Vendedor_Facturas_Pendientes(vendedor):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    # Here we will adding the code to add data
    worksheet_s = workbook.add_worksheet("Facturas pendientes")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    subtitle = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'center',
        'valign': 'top'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'bold': True,
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1
    })

    title_text = "{0}".format(ugettext("Facturas Pendientes"))
    subtitle_text = "{0} {1}".format(ugettext("Vendedor: "), vendedor.nombre)
    worksheet_s.merge_range('B2:D2', title_text, title)
    worksheet_s.merge_range('B3:D3', subtitle_text, title)

    fecha_text = "{0}".format(datetime.now().strftime('%A, %d-%m-%Y / %H:%I'))
    worksheet_s.merge_range('F2:H2', fecha_text, subtitle)

    # Colums Headers
    worksheet_s.write(4, 0, ugettext("No."), header)
    worksheet_s.write(4, 1, ugettext("Factura"), header)
    worksheet_s.write(4, 2, ugettext("Fecha"), header)
    worksheet_s.write(4, 3, ugettext("Cliente"), header)
    worksheet_s.write(4, 4, ugettext("Facturado"), header)
    worksheet_s.write(4, 5, ugettext("Comisión"), header)
    worksheet_s.write(4, 6, ugettext("Pagado"), header)
    worksheet_s.write(4, 7, ugettext("Pendiente"), header)

    # Inicialization columns size for future width
    fecha_col_width = 15
    numerodocumento_col_width = 15
    cliente_col_width = 50
    valores_col_width = 15

    datos = vendedor.facturas_pendientes()
    # Columns Content
    for idx, data in enumerate(datos):
        row = 5 + idx
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write_string(row, 1, data.numero, cell)
        worksheet_s.write(row, 2, data.fecha.strftime('%d-%m-%Y'), cell_center)
        worksheet_s.write_string(row, 3, data.cliente.nombre if data.cliente else "", cell)
        worksheet_s.write_number(row, 4, data.total, cell)
        worksheet_s.write_number(row, 5, data.valor_comision(), cell)
        worksheet_s.write_number(row, 6, data.pagado, cell)
        worksheet_s.write_number(row, 7, data.saldo_pendiente(), cell)

        # Set cell elements width by field length
        if len(data.numero) > numerodocumento_col_width:
            numerodocumento_col_width = len(data.numero)
        if data.cliente and len(data.cliente.nombre) > cliente_col_width:
            cliente_col_width = len(data.cliente.nombre)

    # Resize columns data
    worksheet_s.set_column('B:B', numerodocumento_col_width)
    worksheet_s.set_column('C:C', fecha_col_width)
    worksheet_s.set_column('D:D', cliente_col_width)
    worksheet_s.set_column('E:E', valores_col_width)
    worksheet_s.set_column('F:F', valores_col_width)
    worksheet_s.set_column('G:G', valores_col_width)
    worksheet_s.set_column('H:H', valores_col_width)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data


# Vendedores - Facturas pagadas totalmente
def WriteToExcel_Vendedor_Facturas_Pagadas(vendedor):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    # Here we will adding the code to add data
    worksheet_s = workbook.add_worksheet("Facturas pagadas")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    subtitle = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'center',
        'valign': 'top'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'bold': True,
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1
    })

    title_text = "{0}".format(ugettext("Facturas Pagadas"))
    subtitle_text = "{0} {1}".format(ugettext("Vendedor: "), vendedor.nombre)
    worksheet_s.merge_range('B2:D2', title_text, title)
    worksheet_s.merge_range('B3:D3', subtitle_text, title)

    fecha_text = "{0}".format(datetime.now().strftime('%A, %d-%m-%Y / %H:%I'))
    worksheet_s.merge_range('E2:G2', fecha_text, subtitle)

    # Colums Headers
    worksheet_s.write(4, 0, ugettext("No."), header)
    worksheet_s.write(4, 1, ugettext("Factura"), header)
    worksheet_s.write(4, 2, ugettext("Fecha"), header)
    worksheet_s.write(4, 3, ugettext("Cliente"), header)
    worksheet_s.write(4, 4, ugettext("Facturado"), header)
    worksheet_s.write(4, 5, ugettext("Comisión"), header)
    worksheet_s.write(4, 6, ugettext("Pagado"), header)

    # Inicialization columns size for future width
    fecha_col_width = 15
    numerodocumento_col_width = 15
    cliente_col_width = 50
    valores_col_width = 15

    datos = vendedor.facturas_pagadas()
    # Columns Content
    for idx, data in enumerate(datos):
        row = 5 + idx
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write_string(row, 1, data.numero, cell)
        worksheet_s.write(row, 2, data.fecha.strftime('%d-%m-%Y'), cell_center)
        worksheet_s.write_string(row, 3, data.cliente.nombre if data.cliente else "", cell)
        worksheet_s.write_number(row, 4, data.total, cell)
        worksheet_s.write_number(row, 5, data.valor_comision(), cell)
        worksheet_s.write_number(row, 6, data.pagado, cell)

        # Set cell elements width by field length
        if len(data.numero) > numerodocumento_col_width:
            numerodocumento_col_width = len(data.numero)
        if data.cliente and len(data.cliente.nombre) > cliente_col_width:
            cliente_col_width = len(data.cliente.nombre)

    # Resize columns data
    worksheet_s.set_column('B:B', numerodocumento_col_width)
    worksheet_s.set_column('C:C', fecha_col_width)
    worksheet_s.set_column('D:D', cliente_col_width)
    worksheet_s.set_column('E:E', valores_col_width)
    worksheet_s.set_column('F:F', valores_col_width)
    worksheet_s.set_column('G:G', valores_col_width)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data


# Inventarios
def WriteToExcel_Inventarios_Resumen(datos, categoria=None, ordenar=None, search=None, inicio=None, fin=None):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    # Here we will adding the code to add data
    worksheet_s = workbook.add_worksheet("Inventarios")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    subtitle = workbook.add_format({
        'bold': True,
        'font_size': 11,
        'align': 'center',
        'valign': 'top'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'bold': True,
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1
    })

    filtros = ""
    if categoria:
        filtros += "/ categoria: {0}".format(categoria.nombre)
    if search:
        filtros += "/ búsqueda por: {0}".format(search)
    if ordenar:
        filtros += "/ ordenado de menor a mayor" if ordenar == 1 else "/ ordenado de mayor a menor"
    if inicio and fin:
        filtros += "/ rango de fechas desde {0} al {1}".format(inicio.strftime('%d-%m-%Y'), fin.strftime('%d-%m-%Y'))
    if not categoria and not search and not ordenar and not inicio:
        filtros = "NINGUNO"

    title_text = "{0}".format(ugettext("LISTADO DE INVENTARIOS"))
    subtitle_text = "{0} {1}".format(ugettext("Filtros aplicados: "), filtros)
    worksheet_s.merge_range('B2:F2', title_text, title)
    worksheet_s.merge_range('B3:F3', subtitle_text, title)

    fecha_text = "{0}".format(datetime.now().strftime('%A, %d-%m-%Y / %H:%I'))
    worksheet_s.merge_range('G2:I2', fecha_text, subtitle)

    # Inicialization columns size for future width
    codigo_col_width = 20
    descripcion_col_width = 50
    tipo_col_width = 30
    valores_col_width = 12

    # Colums Headers
    if not inicio and not fin:
        worksheet_s.write(4, 0, ugettext("No."), header)
        worksheet_s.write(4, 1, ugettext("Código"), header)
        worksheet_s.write(4, 2, ugettext("Descripción"), header)
        worksheet_s.write(4, 3, ugettext("Categoría"), header)
        worksheet_s.write(4, 4, ugettext("U.M."), header)
        worksheet_s.write(4, 5, ugettext("Saldo Actual"), header)
        worksheet_s.write(4, 6, ugettext("Costo FOB"), header)
        worksheet_s.write(4, 7, ugettext("Costo CIF"), header)
        worksheet_s.write(4, 8, ugettext("Valor"), header)

        # Columns Content
        for idx, data in enumerate(datos):
            row = 5 + idx
            worksheet_s.write_number(row, 0, idx + 1, cell_center)
            worksheet_s.write_string(row, 1, data.producto.codigo, cell)
            worksheet_s.write_string(row, 2, data.producto.descripcion, cell)
            worksheet_s.write_string(row, 3, data.producto.tipoproducto.nombre if data.producto.tipoproducto else "", cell)
            worksheet_s.write_string(row, 4, data.producto.unidadmedida.nombre if data.producto.unidadmedida else "", cell_center)
            worksheet_s.write_number(row, 5, data.cantidad, cell)
            worksheet_s.write_number(row, 6, data.costofob, cell)
            worksheet_s.write_number(row, 7, data.costo, cell)
            worksheet_s.write_number(row, 8, data.valor, cell)

            # Set cell elements width by field length
            if len(data.producto.codigo) > codigo_col_width:
                codigo_col_width = len(data.producto.codigo)
            if len(data.producto.descripcion) > descripcion_col_width:
                descripcion_col_width = len(data.producto.descripcion)
            if data.producto.tipoproducto and len(data.producto.tipoproducto.nombre) > tipo_col_width:
                tipo_col_width = len(data.producto.tipoproducto.nombre)

        # Resize columns data
        worksheet_s.set_column('B:B', codigo_col_width)
        worksheet_s.set_column('C:C', descripcion_col_width)
        worksheet_s.set_column('D:D', tipo_col_width)
        worksheet_s.set_column('E:E', valores_col_width)
        worksheet_s.set_column('F:F', valores_col_width)
        worksheet_s.set_column('G:G', valores_col_width)
        worksheet_s.set_column('H:H', valores_col_width)
        worksheet_s.set_column('I:I', valores_col_width)
    else:
        worksheet_s.write(4, 0, ugettext("No."), header)
        worksheet_s.write(4, 1, ugettext("Código"), header)
        worksheet_s.write(4, 2, ugettext("Descripción"), header)
        worksheet_s.write(4, 3, ugettext("Categoría"), header)
        worksheet_s.write(4, 4, ugettext("U.M."), header)
        worksheet_s.write(4, 5, ugettext("Saldo Actual"), header)
        worksheet_s.write(4, 6, ugettext("Cant.Vendida"), header)
        worksheet_s.write(4, 7, ugettext("Sug.Import."), header)
        worksheet_s.write(4, 8, ugettext("Costo FOB"), header)
        worksheet_s.write(4, 9, ugettext("Costo CIF"), header)
        worksheet_s.write(4, 10, ugettext("Valor"), header)

        # Columns Content
        for idx, data in enumerate(datos):
            row = 5 + idx
            cantidad_vendida = data.cantidad_vendida_fechas(inicio, fin)
            sugerencia_importacion = cantidad_vendida - data.cantidad if cantidad_vendida > data.cantidad else 0
            worksheet_s.write_number(row, 0, idx + 1, cell_center)
            worksheet_s.write_string(row, 1, data.producto.codigo, cell)
            worksheet_s.write_string(row, 2, data.producto.descripcion, cell)
            worksheet_s.write_string(row, 3, data.producto.tipoproducto.nombre if data.producto.tipoproducto else "", cell)
            worksheet_s.write_string(row, 4, data.producto.unidadmedida.nombre if data.producto.unidadmedida else "", cell_center)
            worksheet_s.write_number(row, 5, data.cantidad, cell)
            worksheet_s.write_number(row, 6, cantidad_vendida, cell)
            worksheet_s.write_number(row, 7, sugerencia_importacion, cell)
            worksheet_s.write_number(row, 8, data.costofob, cell)
            worksheet_s.write_number(row, 9, data.costo, cell)
            worksheet_s.write_number(row, 10, data.valor, cell)

            # Set cell elements width by field length
            if len(data.producto.codigo) > codigo_col_width:
                codigo_col_width = len(data.producto.codigo)
            if data.producto.tipoproducto and len(data.producto.tipoproducto.nombre) > tipo_col_width:
                tipo_col_width = len(data.producto.tipoproducto.nombre)

        # Resize columns data
        worksheet_s.set_column('B:B', codigo_col_width)
        worksheet_s.set_column('C:C', descripcion_col_width)
        worksheet_s.set_column('D:D', tipo_col_width)
        worksheet_s.set_column('E:E', valores_col_width)
        worksheet_s.set_column('F:F', valores_col_width)
        worksheet_s.set_column('G:G', valores_col_width)
        worksheet_s.set_column('H:H', valores_col_width)
        worksheet_s.set_column('I:I', valores_col_width)
        worksheet_s.set_column('J:J', valores_col_width)
        worksheet_s.set_column('K:K', valores_col_width)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data


# Ventas al publico - Resumen (solo cabeceras)
def WriteToExcel_Ventas_Publico_Resumen(datos, search=None, inicio=None, fin=None):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    # Here we will adding the code to add data
    worksheet_s = workbook.add_worksheet("Ventas")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    subtitle = workbook.add_format({
        'bold': True,
        'font_size': 11,
        'align': 'center',
        'valign': 'top'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'bold': True,
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1
    })

    filtros = ""
    if search:
        filtros += "/ búsqueda por: {0}".format(search)
    if inicio and fin:
        filtros += "/ rango de fechas desde {0} al {1}".format(inicio.strftime('%d-%m-%Y'), fin.strftime('%d-%m-%Y'))
    if not search and not inicio:
        filtros = "NINGUNO"

    title_text = "{0}".format(ugettext("VENTAS AL PUBLICO"))
    subtitle_text = "{0} {1}".format(ugettext("Filtros aplicados: "), filtros)
    worksheet_s.merge_range('B2:F2', title_text, title)
    worksheet_s.merge_range('B3:F3', subtitle_text, title)

    fecha_text = "{0}".format(datetime.now().strftime('%A, %d-%m-%Y / %H:%I'))
    worksheet_s.merge_range('K2:M2', fecha_text, subtitle)

    # Colums Headers
    worksheet_s.write(4, 0, ugettext("No."), header)
    worksheet_s.write(4, 1, ugettext("Código"), header)
    worksheet_s.write(4, 2, ugettext("Fecha"), header)
    worksheet_s.write(4, 3, ugettext("No. Doc."), header)
    worksheet_s.write(4, 4, ugettext("Cliente"), header)
    worksheet_s.write(4, 5, ugettext("Subtotal"), header)
    worksheet_s.write(4, 6, ugettext("IVA"), header)
    worksheet_s.write(4, 7, ugettext("Total"), header)
    worksheet_s.write(4, 8, ugettext("Cobrado"), header)
    worksheet_s.write(4, 9, ugettext("Pendiente"), header)
    worksheet_s.write(4, 10, ugettext("Retenido"), header)
    worksheet_s.write(4, 11, ugettext("Por Pagar"), header)
    worksheet_s.write(4, 12, ugettext("Utilidad"), header)
    worksheet_s.write(4, 13, ugettext("Items"), header)
    worksheet_s.write(4, 14, ugettext("Vendedor"), header)
    worksheet_s.write(4, 15, ugettext("Estado"), header)

    # Inicialization columns size for future width
    fecha_col_width = 15
    numerodocumento_col_width = 15
    cliente_col_width = 40
    valores_col_width = 12
    vendedor_col_width = 15
    estado_col_width = 15

    # Columns Content
    for idx, data in enumerate(datos):
        row = 5 + idx
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write_string(row, 1, data.repr_id(), cell)
        worksheet_s.write(row, 2, data.fecha.strftime('%d-%m-%Y'), cell_center)
        worksheet_s.write_string(row, 3, data.numero, cell)
        worksheet_s.write_string(row, 4, data.cliente.nombre if data.cliente else "", cell)
        worksheet_s.write_number(row, 5, data.subtotal, cell)
        worksheet_s.write_number(row, 6, data.iva, cell)
        worksheet_s.write_number(row, 7, data.total, cell)
        worksheet_s.write_number(row, 8, data.pagado, cell)
        worksheet_s.write_number(row, 9, data.saldo_pendiente(), cell)
        worksheet_s.write_number(row, 10, data.valor_total_retenido, cell)
        worksheet_s.write_number(row, 11, data.valor_total_por_pagar(), cell)
        worksheet_s.write_number(row, 12, data.utilidad_publico(), cell)
        worksheet_s.write_number(row, 13, data.cantidad_productos(), cell_center)
        worksheet_s.write_string(row, 14, data.vendedor.usuario.username if data.vendedor else "", cell_center)
        worksheet_s.write_string(row, 15, data.mi_estado(), cell_center)

        # Set cell elements width by field length
        if len(data.numero) > numerodocumento_col_width:
            numerodocumento_col_width = len(data.numero)
        if data.cliente and len(data.cliente.nombre) > cliente_col_width:
            cliente_col_width = len(data.cliente.nombre)
        if len(data.mi_estado()) > estado_col_width:
            estado_col_width = len(data.mi_estado())

    # Resize columns data
    worksheet_s.set_column('C:C', fecha_col_width)
    worksheet_s.set_column('D:D', numerodocumento_col_width)
    worksheet_s.set_column('E:E', cliente_col_width)
    worksheet_s.set_column('F:F', valores_col_width)
    worksheet_s.set_column('G:G', valores_col_width)
    worksheet_s.set_column('H:H', valores_col_width)
    worksheet_s.set_column('I:I', valores_col_width)
    worksheet_s.set_column('J:J', valores_col_width)
    worksheet_s.set_column('K:K', valores_col_width)
    worksheet_s.set_column('L:L', valores_col_width)
    worksheet_s.set_column('M:M', valores_col_width)
    worksheet_s.set_column('O:O', vendedor_col_width)
    worksheet_s.set_column('P:P', estado_col_width)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data


# Ventas al publico - Detallado (incluye el detalle de la venta)
def WriteToExcel_Ventas_Publico_Detallado(venta):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    # Here we will adding the code to add data
    worksheet_s = workbook.add_worksheet("Detalles de venta al publico")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    subtitle = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'center',
        'valign': 'top'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'bold': True,
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1
    })

    title_text = "{0} {1}".format(ugettext("Detalle de la Venta al público: "), venta.repr_id())
    subtitle_text = "{0} {1} {2} {3}".format(ugettext("Cliente: "),
                                             venta.cliente.nombre,
                                             ugettext("Documento: "),
                                             venta.numero)
    worksheet_s.merge_range('B2:C2', title_text, title)
    worksheet_s.merge_range('B3:C3', subtitle_text, subtitle)

    fecha_text = "{0}".format(datetime.now().strftime('%A, %d-%m-%Y / %H:%I'))
    worksheet_s.merge_range('D2:F2', fecha_text, subtitle)

    # Colums Headers
    worksheet_s.write(4, 0, ugettext("No."), header)
    worksheet_s.write(4, 1, ugettext("Código"), header)
    worksheet_s.write(4, 2, ugettext("Descripción"), header)
    worksheet_s.write(4, 3, ugettext("Cantidad"), header)
    worksheet_s.write(4, 4, ugettext("Precio"), header)
    worksheet_s.write(4, 5, ugettext("Valor"), header)

    # Inicialization columns size for future width
    codigo_col_width = 25
    descripcion_col_width = 75
    valores_col_width = 10

    datos = venta.detalles.all()
    # Columns Content
    for idx, data in enumerate(datos):
        row = 5 + idx
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write_string(row, 1, data.producto.codigo, cell)
        worksheet_s.write_string(row, 2, data.producto.descripcion, cell)
        worksheet_s.write_number(row, 3, data.cantidad, cell)
        worksheet_s.write_number(row, 4, data.precio, cell)
        worksheet_s.write_number(row, 5, data.valor, cell)

        # Set cell elements width by field length
        if len(data.producto.codigo) > codigo_col_width:
            codigo_col_width = len(data.producto.codigo)
        if len(data.producto.descripcion) > descripcion_col_width:
            descripcion_col_width = len(data.producto.descripcion)

    # Resize columns data
    worksheet_s.set_column('B:B', codigo_col_width)
    worksheet_s.set_column('C:C', descripcion_col_width)
    worksheet_s.set_column('D:D', valores_col_width)
    worksheet_s.set_column('E:E', valores_col_width)
    worksheet_s.set_column('F:F', valores_col_width)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data


# Resumen de compra en venta al publico
def WriteToExcel_CxP_Publico(datos, proveedor=None, filtro=None):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    # Here we will adding the code to add data
    worksheet_s = workbook.add_worksheet("Ventas")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    subtitle = workbook.add_format({
        'bold': True,
        'font_size': 11,
        'align': 'center',
        'valign': 'top'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'bold': True,
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1
    })

    filtros = ""
    if proveedor:
        filtros += "Proveedor: {0}".format(proveedor.nombre_simple())
    if filtro:
        if filtro == 1:
            filtros += " /solo cuentas por pagar"
        if filtro == 2:
            filtros += " /solo facturas totalmente pagadas"
    if not proveedor and not filtro:
        filtros = "NINGUNO"

    title_text = "{0}".format(ugettext("RESUMEN DE COMPRA EN VENTA AL PUBLICO"))
    subtitle_text = "{0} {1}".format(ugettext("Filtros aplicados: "), filtros)
    worksheet_s.merge_range('B2:F2', title_text, title)
    worksheet_s.merge_range('B3:F3', subtitle_text, title)

    fecha_text = "{0}".format(datetime.now().strftime('%A, %d-%m-%Y / %H:%I'))
    worksheet_s.merge_range('I2:K2', fecha_text, subtitle)

    # Colums Headers
    worksheet_s.write(4, 0, ugettext("No."), header)
    worksheet_s.write(4, 1, ugettext("Proveedor"), header)
    worksheet_s.write(4, 2, ugettext("No.Fact."), header)
    worksheet_s.write(4, 3, ugettext("Fecha Fact."), header)
    worksheet_s.write(4, 4, ugettext("Valor Fact."), header)
    worksheet_s.write(4, 5, ugettext("Valor Ret."), header)
    worksheet_s.write(4, 6, ugettext("Valor Pagar."), header)
    worksheet_s.write(4, 7, ugettext("Pagado"), header)
    worksheet_s.write(4, 8, ugettext("No.Fact."), header)
    worksheet_s.write(4, 9, ugettext("Fecha Fact."), header)
    worksheet_s.write(4, 10, ugettext("Cliente"), header)

    # Inicialization columns size for future width
    fecha_col_width = 15
    numerodocumento_col_width = 15
    cliente_col_width = 40
    valores_col_width = 12

    # Columns Content
    for idx, data in enumerate(datos):
        row = 5 + idx
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write_string(row, 1, data.proveedor.nombre_simple() if data.proveedor else "", cell)
        worksheet_s.write_string(row, 2, data.factura_prov, cell_center)
        worksheet_s.write(row, 3, data.fecha_factura_prov.strftime('%d-%m-%Y'), cell_center)
        worksheet_s.write_number(row, 4, data.valor_factura_prov, cell)
        worksheet_s.write_number(row, 5, data.valor_retenido_prov, cell)
        worksheet_s.write_number(row, 6, data.valor_apagar_prov, cell)
        worksheet_s.write_string(row, 7, data.repr_pagado(), cell_center)
        worksheet_s.write_string(row, 8, data.factura.numero if data.factura else "", cell_center)
        worksheet_s.write(row, 9, data.factura.fecha.strftime('%d-%m-%Y'), cell_center)
        worksheet_s.write_string(row, 10, data.factura.cliente.nombre if data.factura and data.factura.cliente else "", cell)

        # Set cell elements width by field length
        if len(data.factura_prov) > numerodocumento_col_width:
            numerodocumento_col_width = len(data.factura_prov)
        if data.factura.cliente and len(data.factura.cliente.nombre) > cliente_col_width:
            cliente_col_width = len(data.factura.cliente.nombre)
        if data.proveedor and len(data.proveedor.nombre) > cliente_col_width:
            cliente_col_width = len(data.proveedor.nombre)

    # Resize columns data
    worksheet_s.set_column('B:B', cliente_col_width)
    worksheet_s.set_column('C:C', numerodocumento_col_width)
    worksheet_s.set_column('D:D', fecha_col_width)
    worksheet_s.set_column('E:E', valores_col_width)
    worksheet_s.set_column('F:F', valores_col_width)
    worksheet_s.set_column('G:G', valores_col_width)

    worksheet_s.set_column('I:I', numerodocumento_col_width)
    worksheet_s.set_column('J:J', fecha_col_width)
    worksheet_s.set_column('K:K', cliente_col_width)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data


# Resumen de comisionistas en venta al publico
def WriteToExcel_Comisionistas_Publico(datos, proveedor=None, filtro=None):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)

    # Here we will adding the code to add data
    worksheet_s = workbook.add_worksheet("Ventas")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    subtitle = workbook.add_format({
        'bold': True,
        'font_size': 11,
        'align': 'center',
        'valign': 'top'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'bold': True,
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1
    })
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1
    })

    filtros = ""
    if proveedor:
        filtros += "Comisionista: {0}".format(proveedor.nombre_simple())
    if filtro:
        if filtro == 1:
            filtros += " /solo comisiones por pagar"
        if filtro == 2:
            filtros += " /solo comisiones totalmente pagadas"
    if not proveedor and not filtro:
        filtros = "NINGUNO"

    title_text = "{0}".format(ugettext("RESUMEN DE COMISIONISTAS EN VENTA AL PUBLICO"))
    subtitle_text = "{0} {1}".format(ugettext("Filtros aplicados: "), filtros)
    worksheet_s.merge_range('B2:E2', title_text, title)
    worksheet_s.merge_range('B3:E3', subtitle_text, title)

    fecha_text = "{0}".format(datetime.now().strftime('%A, %d-%m-%Y / %H:%I'))
    worksheet_s.merge_range('F2:G2', fecha_text, subtitle)

    # Colums Headers
    worksheet_s.write(4, 0, ugettext("No."), header)
    worksheet_s.write(4, 1, ugettext("Comisionista"), header)
    worksheet_s.write(4, 2, ugettext("Valor"), header)
    worksheet_s.write(4, 3, ugettext("Pagado"), header)
    worksheet_s.write(4, 4, ugettext("No.Fact."), header)
    worksheet_s.write(4, 5, ugettext("Fecha Fact."), header)
    worksheet_s.write(4, 6, ugettext("Cliente"), header)

    # Inicialization columns size for future width
    fecha_col_width = 15
    numerodocumento_col_width = 15
    cliente_col_width = 40
    valores_col_width = 12

    # Columns Content
    for idx, data in enumerate(datos):
        row = 5 + idx
        worksheet_s.write_number(row, 0, idx + 1, cell_center)
        worksheet_s.write_string(row, 1, data.comisionista.nombre_simple() if data.comisionista else "", cell)
        worksheet_s.write_number(row, 2, data.valor, cell)
        worksheet_s.write_string(row, 3, data.repr_pagado(), cell_center)
        worksheet_s.write_string(row, 4, data.factura.numero if data.factura else "", cell_center)
        worksheet_s.write(row, 5, data.factura.fecha.strftime('%d-%m-%Y'), cell_center)
        worksheet_s.write_string(row, 6, data.factura.cliente.nombre if data.factura and data.factura.cliente else "", cell)

        # Set cell elements width by field length
        if data.factura.cliente and len(data.factura.cliente.nombre) > cliente_col_width:
            cliente_col_width = len(data.factura.cliente.nombre)
        if data.comisionista and len(data.comisionista.nombre) > cliente_col_width:
            cliente_col_width = len(data.comisionista.nombre)

    # Resize columns data
    worksheet_s.set_column('B:B', cliente_col_width)
    worksheet_s.set_column('C:C', valores_col_width)
    worksheet_s.set_column('E:E', numerodocumento_col_width)
    worksheet_s.set_column('F:F', fecha_col_width)
    worksheet_s.set_column('G:G', cliente_col_width)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data
