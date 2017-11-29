addProveedor = function() {
    $("#proveedorpanel").modal({backdrop: 'static', maxHeight: ($(window).height()*2)/3});
    $("#id_proveedor-identificacion").val("");
    $("#id_proveedor-nombre").val("");
    $("#id_proveedor-apellidos").val("");
    $("#id_proveedor-alias").val("");
    $("#id_proveedor-direccion").val("");
    $("#id_proveedor-canton").val("");
    $("#id_proveedor-provincia").val("");
    $("#id_proveedor-telefono").val("");
    $("#id_proveedor-celular").val("");
    $("#id_proveedor-email").val("");
    $("#id_proveedor-fax").val("");

    $("#proveedorpanel").modal("show");

    return false;
};

cerrarAdicionarProveedor = function() {
    $("#proveedorpanel").modal("hide");
    return false;
};

$(function() {
    $("#proveedorpanel input").addClass("input-block-level");
    chequeaProveedor = function() {
        if ($("#id_proveedor-personanatural").is(':checked')) {
            $("#id_proveedor-apellidos").attr("disabled", false);
            $("#id_proveedor-alias").attr("disabled", true);
            $("#id_proveedor-tipoidentificacion").val("0");
            $("#id_proveedor-tipoidentificacion").get(0).item(2).disabled = false;
            $("#id_proveedor-tipoidentificacion").get(0).item(3).disabled = false;
        } else {
            $("#id_proveedor-apellidos").attr("disabled", true);
            $("#id_proveedor-apellidos").val("");
            $("#id_proveedor-alias").attr("disabled", false);
            $("#id_proveedor-tipoidentificacion").val("1");
            $("#id_proveedor-tipoidentificacion").get(0).item(2).disabled = true;
            $("#id_proveedor-tipoidentificacion").get(0).item(3).disabled = true;
        }
        chequeaDocumento();
    };

    chequeaDocumento = function () {
        if ($("#id_proveedor-tipoidentificacion").val()=='1') {
            $("#id_proveedor-identificacion").mask("9999999999999");
        }
        if ($("#id_proveedor-tipoidentificacion").val()=='2') {
            $("#id_proveedor-identificacion").mask("9999999999");
        }
        if ($("#id_proveedor-tipoidentificacion").val()=='3') {
            $("#id_proveedor-identificacion").unmask();
        }
    };

    $("#id_proveedor-tipoidentificacion").change(chequeaDocumento);
    $("#id_proveedor-personanatural").change(chequeaProveedor);
    chequeaProveedor();
    chequeaDocumento();

    $("#proveedorpanel .boton2").click(cerrarAdicionarProveedor).show();
    $("#proveedorpanel .boton1").click(adicionarProveedor);
});

adicionarProveedor = function() {
    var valores = {};
    valores['personanatural'] = $("#id_proveedor-personanatural").is(":checked");
    valores['tipoidentificacion'] = $("#id_proveedor-tipoidentificacion").val();
    valores['identificacion'] = $("#id_proveedor-identificacion").val();
    valores['nombre'] = $("#id_proveedor-nombre").val();
    valores['apellidos'] = $("#id_proveedor-apellidos").val();
    valores['alias'] = $("#id_proveedor-alias").val();
    valores['direccion'] = $("#id_proveedor-direccion").val();
    valores['canton'] = $("#id_proveedor-canton").val();
    valores['provincia'] = $("#id_proveedor-provincia").val();
    valores['telefono'] = $("#id_proveedor-telefono").val();
    valores['celular'] = $("#id_proveedor-celular").val();
    valores['email'] = $("#id_proveedor-email").val();
    valores['fax'] = $("#id_proveedor-fax").val();
    valores['action'] = 'addjson';
    $.post("/proveedores", valores, function(data) {
        if (data.result=='ok') {
            cerrarAdicionarProveedor();
        } else {
            $($("#id_proveedor-identificacion").get(0).parentNode).find(".help-text").html("Esta identificacion ya existe");
        }
    }, "json");

};