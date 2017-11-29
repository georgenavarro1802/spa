from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from inv.forms import CajeroForm
from inv.funciones import salva_auditoria, MiPaginador, url_back, mensaje_excepcion, bad_json, ok_json
from inv.models import Cajero
from inv.views import addUserData
from spa.settings import ACCION_ADICIONAR, ACCION_MODIFICAR, ACCION_ELIMINAR, DEFAULT_PASSWORD, CAJAS_GROUP_ID


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': u'Gestión de Cajeros'}
    addUserData(request, data)

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            f = CajeroForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        cedula = f.cleaned_data['cedula']
                        usuario_nombre = f.cleaned_data['usuario']
                        if Cajero.objects.filter(cedula=cedula).exists():
                            return bad_json(mensaje=u"Ya existe un cajero registrado con ese número de cedula.")
                        if User.objects.filter(username=usuario_nombre).exists():
                            return bad_json(mensaje=u"Ya existe ese nombre de usuario en el sistema favor de corregir.")

                        cajero = Cajero(cedula=cedula,
                                        nombre=f.cleaned_data['nombre'],
                                        direccion=f.cleaned_data['direccion'],
                                        telefono=f.cleaned_data['telefono'],
                                        email=f.cleaned_data['email'])
                        cajero.save()

                        user = User.objects.create_user(usuario_nombre, cajero.email, DEFAULT_PASSWORD)
                        user.username = user.username.lower()
                        user.save()
                        cajero.usuario = user
                        cajero.save()
                        g = Group.objects.get(pk=CAJAS_GROUP_ID)
                        g.user_set.add(user)
                        g.save()
                        salva_auditoria(request, cajero, ACCION_ADICIONAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'edit':
            cajero = Cajero.objects.get(pk=request.POST['id'])
            f = CajeroForm(request.POST)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        cedula = f.cleaned_data['cedula']
                        usuario_nombre = f.cleaned_data['usuario']
                        if Cajero.objects.filter(cedula=cedula).exclude(id=cajero.id).exists():
                            return bad_json(mensaje=u"Ya existe un cajero registrado con ese número de cedula.")
                        if User.objects.filter(username=usuario_nombre).exclude(cajero__id=cajero.id).exists():
                            return bad_json(mensaje=u"Ya existe ese nombre de usuario en el sistema favor de corregir.")

                        cajero.cedula = cedula
                        cajero.nombre = f.cleaned_data['nombre']
                        cajero.direccion = f.cleaned_data['direccion']
                        cajero.telefono = f.cleaned_data['telefono']
                        cajero.email = f.cleaned_data['email']
                        cajero.save()
                        cajero.usuario.username = usuario_nombre
                        cajero.usuario.save()
                        salva_auditoria(request, cajero, ACCION_MODIFICAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=2)
            else:
                return bad_json(error=2)

        elif action == 'delete':
            try:
                cajero = Cajero.objects.get(pk=request.POST['id'])
                with transaction.atomic():
                    salva_auditoria(request, cajero, ACCION_ELIMINAR)
                    cajero.delete()
                    return ok_json()

            except Exception:
                return bad_json(error=3)

        elif action == 'resetear':
            try:
                cajero = Cajero.objects.get(pk=request.POST['id'])
                with transaction.atomic():
                    user = cajero.usuario
                    user.set_password(DEFAULT_PASSWORD)
                    user.save()
                    salva_auditoria(request, cajero, ACCION_MODIFICAR)
                    return ok_json()

            except Exception:
                return bad_json(error=2)

        return bad_json(error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    data['title'] = u'Crear Cajero'
                    data['form'] = CajeroForm()
                    return render_to_response("cajeros/add.html", data)
                except Exception as ex:
                    pass

            elif action == 'edit':
                try:
                    data['title'] = u'Editar Cajero'
                    data['cajero'] = cajero = Cajero.objects.get(pk=request.GET['id'])
                    data['form'] = CajeroForm(initial={'cedula': cajero.cedula,
                                                       'nombre': cajero.nombre,
                                                       'direccion': cajero.direccion,
                                                       'telefono': cajero.telefono,
                                                       'email': cajero.email,
                                                       'usuario': cajero.usuario.username})
                    return render_to_response("cajeros/edit.html", data)
                except Exception as ex:
                    pass

            elif action == 'delete':
                try:
                    data['title'] = u'Borrar cajero'
                    data['cajero'] = Cajero.objects.get(pk=request.GET['id'])
                    return render_to_response("cajeros/delete.html", data)
                except Exception as ex:
                    pass

            elif action == 'resetear':
                try:
                    data['title'] = u'Resetear clave del cajero'
                    data['cajero'] = Cajero.objects.get(pk=request.GET['id'])
                    return render_to_response("cajeros/resetear.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:
            search = None

            if 's' in request.GET:
                search = request.GET['s']
            if search:
                cajeros = Cajero.objects.filter(Q(nombre__icontains=search) |
                                                Q(cedula__icontains=search) |
                                                Q(usuario__username__icontains=search))
            else:
                cajeros = Cajero.objects.all()

            paging = MiPaginador(cajeros, 30)
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
            data['cajeros'] = page.object_list
            return render_to_response("cajeros/view.html", data)
