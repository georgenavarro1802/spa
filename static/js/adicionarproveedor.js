adicionarEntidad = function() {
    $("#entidadpanel").modal({backdrop: 'static', maxHeight: ($(window).height()*2)/3});
    $("#id_entidad-identificacion").val("");
    $("#id_entidad-nombre").val("");
    $("#id_entidad-apellidos").val("");
    $("#id_entidad-alias").val("");
    $("#id_entidad-direccion").val("");
    $("#id_entidad-canton").val("");
    $("#id_entidad-provincia").val("");
    $("#id_entidad-telefono").val("");
    $("#id_entidad-celular").val("");
    $("#id_entidad-email").val("");
    $("#id_entidad-fax").val("");

    $("#entidadpanel").modal("show");

    return false;
};

cerrarAdicionarEntidad = function() {
    $("#entidadpanel").modal("hide");
    return false;
};

$(function() {
    $("#entidadpanel input").addClass("input-block-level");
    chequeaProveedor = function() {
        if ($("#id_entidad-personanatural").is(':checked')) {
            $("#id_entidad-apellidos").attr("disabled", false);
            $("#id_entidad-alias").attr("disabled", true);
            $("#id_entidad-tipoidentificacion").val("0");
            $("#id_entidad-tipoidentificacion").get(0).item(2).disabled = false;
            $("#id_entidad-tipoidentificacion").get(0).item(3).disabled = false;
        } else {
            $("#id_entidad-apellidos").attr("disabled", true);
            $("#id_entidad-apellidos").val("");
            $("#id_entidad-alias").attr("disabled", false);
            $("#id_entidad-tipoidentificacion").val("1");
            $("#id_entidad-tipoidentificacion").get(0).item(2).disabled = true;
            $("#id_entidad-tipoidentificacion").get(0).item(3).disabled = true;
        }
        chequeaDocumento();
    }

    chequeaDocumento = function () {
        if ($("#id_entidad-tipoidentificacion").val()=='1') {
            $("#id_entidad-identificacion").mask("9999999999999");
        }
        if ($("#id_entidad-tipoidentificacion").val()=='2') {
            $("#id_entidad-identificacion").mask("9999999999");
        }
        if ($("#id_entidad-tipoidentificacion").val()=='3') {
            $("#id_entidad-identificacion").unmask();
        }
    }

    $("#id_entidad-tipoidentificacion").change(chequeaDocumento);
    $("#id_entidad-personanatural").change(chequeaProveedor);
    chequeaProveedor();
    chequeaDocumento();

    $("#entidadpanel .boton2").click(cerrarAdicionarEntidad).show();
    $("#entidadpanel .boton1").click(adicionarProveedor);
});

adicionarProveedor = function() {
    var valores = {};
    valores['personanatural'] = $("#id_entidad-personanatural").is(":checked");
    valores['tipoidentificacion'] = $("#id_entidad-tipoidentificacion").val();
    valores['identificacion'] = $("#id_entidad-identificacion").val();
    valores['nombre'] = $("#id_entidad-nombre").val();
    valores['apellidos'] = $("#id_entidad-apellidos").val();
    valores['alias'] = $("#id_entidad-alias").val();
    valores['direccion'] = $("#id_entidad-direccion").val();
    valores['canton'] = $("#id_entidad-canton").val();
    valores['provincia'] = $("#id_entidad-provincia").val();
    valores['telefono'] = $("#id_entidad-telefono").val();
    valores['celular'] = $("#id_entidad-celular").val();
    valores['email'] = $("#id_entidad-email").val();
    valores['fax'] = $("#id_entidad-fax").val();
    valores['action'] = 'addjson';
    $.post("/proveedores", valores, function(data) {
        if (data.result=='ok') {
            cerrarAdicionarEntidad();
        } else {
            $($("#id_entidad-identificacion").get(0).parentNode).find(".help-text").html("Esta identificacion ya existe");
        }
    }, "json");



};