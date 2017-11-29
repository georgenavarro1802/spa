from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from inv.forms import ProveedorForm
from inv.funciones import salva_auditoria, MiPaginador, generar_nombre, url_back, mensaje_excepcion, bad_json, ok_json
from inv.models import Proveedor
from inv.views import addUserData
from spa.settings import ACCION_ADICIONAR, ACCION_MODIFICAR, ACCION_ELIMINAR


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': u'Gestión de Proveedores'}
    addUserData(request, data)
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            f = ProveedorForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        identificacion = f.cleaned_data['identificacion']
                        if identificacion and Proveedor.objects.filter(identificacion=identificacion).exists():
                            return bad_json(mensaje=u"Ya existe un proveedor con ese número de identificacion.")

                        proveedor = Proveedor(identificacion=f.cleaned_data['identificacion'],
                                              nombre=f.cleaned_data['nombre'],
                                              alias=f.cleaned_data['alias'],
                                              pais=f.cleaned_data['pais'],
                                              direccion=f.cleaned_data['direccion'],
                                              telefono=f.cleaned_data['telefono'],
                                              celular=f.cleaned_data['celular'],
                                              email=f.cleaned_data['email'],
                                              fax=f.cleaned_data['fax'])
                        proveedor.save()

                        if 'logo' in request.FILES:
                            newlogo = request.FILES['logo']
                            newlogo._name = generar_nombre("logoprov_", newlogo._name)
                            proveedor.logo = newlogo
                            proveedor.save()
                        salva_auditoria(request, proveedor, ACCION_ADICIONAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'edit':
            proveedor = Proveedor.objects.get(pk=request.POST['id'])
            f = ProveedorForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        identificacion = f.cleaned_data['identificacion']
                        if identificacion and Proveedor.objects.filter(identificacion=identificacion).exclude(id=proveedor.id).exists():
                            return bad_json(mensaje=u"Ya existe un proveedor con ese número de identificacion.")
                        proveedor.identificacion = f.cleaned_data['identificacion']
                        proveedor.nombre = f.cleaned_data['nombre']
                        proveedor.alias = f.cleaned_data['alias']
                        proveedor.direccion = f.cleaned_data['direccion']
                        proveedor.pais = f.cleaned_data['pais']
                        proveedor.telefono = f.cleaned_data['telefono']
                        proveedor.celular = f.cleaned_data['celular']
                        proveedor.email = f.cleaned_data['email']
                        proveedor.fax = f.cleaned_data['fax']
                        proveedor.save()

                        if 'logo' in request.FILES:
                            newlogo = request.FILES['logo']
                            newlogo._name = generar_nombre("logoprov_", newlogo._name)
                            proveedor.logo = newlogo
                            proveedor.save()
                        salva_auditoria(request, proveedor, ACCION_MODIFICAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=2)
            else:
                return bad_json(error=2)

        elif action == 'delete':
            proveedor = Proveedor.objects.get(pk=request.POST['id'])
            try:
                with transaction.atomic():
                    salva_auditoria(request, proveedor, ACCION_ELIMINAR)
                    proveedor.delete()
                    return ok_json()
            except Exception:
                return bad_json(error=3)

        return bad_json(error=0)

    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    data['title'] = u'Adicionar Proveedor'
                    data['form'] = ProveedorForm()
                    return render_to_response("proveedores/add.html", data)

                except Exception as ex:
                    pass

            elif action == 'edit':
                try:
                    data['title'] = u'Editar Proveedor'
                    data['proveedor'] = proveedor = Proveedor.objects.get(pk=request.GET['id'])
                    data['form'] = ProveedorForm(initial={'identificacion': proveedor.identificacion,
                                                          'nombre': proveedor.nombre,
                                                          'alias': proveedor.alias,
                                                          'direccion': proveedor.direccion,
                                                          'pais': proveedor.pais,
                                                          'telefono': proveedor.telefono,
                                                          'celular': proveedor.celular,
                                                          'email': proveedor.email,
                                                          'fax': proveedor.fax,
                                                          'logo': proveedor.logo})
                    return render_to_response("proveedores/edit.html", data)

                except Exception as ex:
                    pass

            elif action == 'delete':
                try:
                    data['title'] = u'Borrar Proveedor'
                    data['proveedor'] = Proveedor.objects.get(pk=request.GET['id'])
                    return render_to_response("proveedores/delete.html", data)

                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:
            search = None

            if 's' in request.GET:
                search = request.GET['s']

            proveedores = Proveedor.objects.all()
            if search:
                proveedores = proveedores.filter(Q(nombre__icontains=search) |
                                                 Q(alias__icontains=search) |
                                                 Q(identificacion__icontains=search))

            paging = MiPaginador(proveedores, 30)
            p = 1
            try:
                if 'page' in request.GET:
                    p = int(request.GET['page'])
                page = paging.page(p)
            except:
                page = paging.page(1)
            data['paging'] = paging
            data['rangospaging'] = paging.rangos_paginado(p)
            data['page'] = page
            data['search'] = search if search else ""
            data['proveedores'] = page.object_list
            return render_to_response("proveedores/proveedores.html", data)
