from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from inv.forms import ClienteForm
from inv.funciones import salva_auditoria, MiPaginador, mensaje_excepcion, url_back, generar_nombre, bad_json, ok_json
from inv.models import Cliente
from inv.views import addUserData
from spa.settings import (ACCION_ADICIONAR, ACCION_MODIFICAR, ACCION_ELIMINAR, CLIENTES_GROUP_ID, DEFAULT_PASSWORD)


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': u'Gestión de Clientes'}
    addUserData(request, data)
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            f = ClienteForm(request.POST, request.FILES)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        tipo = int(f.cleaned_data['tipo'])
                        ruc = f.cleaned_data['ruc']
                        identificacion = f.cleaned_data['identificacion']
                        usuario_nombre = f.cleaned_data['usuario']
                        if identificacion and Cliente.objects.filter(identificacion=identificacion).exists():
                            return bad_json(mensaje=u"Ya existe un cliente con ese número de identificación.")
                        if ruc and Cliente.objects.filter(ruc=ruc).exists():
                            return bad_json(mensaje=u"Ya existe un cliente con ese número de RUC.")
                        if User.objects.filter(username=usuario_nombre).exists():
                            return bad_json(mensaje=u"Ya existe ese nombre de usuario en el sistema.")

                        cliente = Cliente(tipo=tipo,
                                          identificacion=identificacion,
                                          nombre=f.cleaned_data['nombre'],
                                          domicilio=f.cleaned_data['domicilio'],
                                          fecha_nacimiento=f.cleaned_data['fecha_nacimiento'],
                                          email=f.cleaned_data['email'],
                                          telefono=f.cleaned_data['telefono'],
                                          celular=f.cleaned_data['celular'],
                                          # corporativos
                                          ruc=f.cleaned_data['ruc'],
                                          razon_social=f.cleaned_data['razon_social'],
                                          representante_legal=f.cleaned_data['representante_legal'],
                                          # especificos
                                          alergias=f.cleaned_data['alergias'],
                                          caracteristicas_fisicas=f.cleaned_data['caracteristicas_fisicas'],
                                          tipo_cabello=f.cleaned_data['tipo_cabello'],
                                          tipo_piel=f.cleaned_data['tipo_piel'],
                                          oportunidades_servicios=f.cleaned_data['oportunidades_servicios'])
                        cliente.save()

                        if 'foto' in request.FILES:
                            newfile = request.FILES['foto']
                            newfile._name = generar_nombre("foto_", newfile._name)
                            cliente.foto = newfile
                            cliente.save()

                        user = User.objects.create_user(usuario_nombre, cliente.email, DEFAULT_PASSWORD)
                        user.username = user.username.lower()
                        user.save()
                        cliente.usuario = user
                        cliente.save()
                        g = Group.objects.get(pk=CLIENTES_GROUP_ID)
                        g.user_set.add(user)
                        g.save()
                        salva_auditoria(request, cliente, ACCION_ADICIONAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=1)
            else:
                return bad_json(error=1)

        elif action == 'edit':
            cliente = Cliente.objects.get(pk=request.POST['id'])
            f = ClienteForm(request.POST, request.FILES)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        tipo = int(f.cleaned_data['tipo'])
                        ruc = f.cleaned_data['ruc']
                        identificacion = f.cleaned_data['identificacion']
                        usuario_nombre = f.cleaned_data['usuario']
                        if identificacion and Cliente.objects.filter(identificacion=identificacion).exclude(id=cliente.id).exists():
                            return bad_json(mensaje=u"Ya existe un cliente con ese número de identificación.")
                        if ruc and Cliente.objects.filter(ruc=ruc).exclude(id=cliente.id).exists():
                            return bad_json(mensaje=u"Ya existe un cliente con ese número de RUC.")
                        if User.objects.filter(username=usuario_nombre).exclude(cliente__id=cliente.id).exists():
                            return bad_json(mensaje=u"Ya existe ese nombre de usuario en el sistema.")

                        if not cliente.usuario:
                            user = User.objects.create_user(usuario_nombre, cliente.email, DEFAULT_PASSWORD)
                            user.username = user.username.lower()
                            user.save()
                            cliente.usuario = user
                            cliente.save()
                            g = Group.objects.get(pk=CLIENTES_GROUP_ID)
                            g.user_set.add(user)
                            g.save()
                        else:
                            cliente.usuario.username = usuario_nombre
                            cliente.usuario.save()

                        cliente.tipo = tipo
                        cliente.nombre = f.cleaned_data['nombre']
                        cliente.identificacion = f.cleaned_data['identificacion']
                        cliente.domicilio = f.cleaned_data['domicilio']
                        cliente.fecha_nacimiento = f.cleaned_data['fecha_nacimiento']
                        cliente.email = f.cleaned_data['email']
                        cliente.telefono = f.cleaned_data['telefono']
                        cliente.celular = f.cleaned_data['celular']
                        # corporativos
                        cliente.ruc = f.cleaned_data['ruc']
                        cliente.razon_social = f.cleaned_data['razon_social']
                        cliente.representante_legal = f.cleaned_data['representante_legal']
                        # especificos
                        cliente.alergias = f.cleaned_data['alergias']
                        cliente.caracteristicas_fisicas = f.cleaned_data['caracteristicas_fisicas']
                        cliente.tipo_cabello = f.cleaned_data['tipo_cabello']
                        cliente.tipo_piel = f.cleaned_data['tipo_piel']
                        cliente.oportunidades_servicios = f.cleaned_data['oportunidades_servicios']

                        cliente.save()
                        if 'foto' in request.FILES:
                            newfile = request.FILES['foto']
                            newfile._name = generar_nombre("foto_", newfile._name)
                            cliente.foto = newfile
                            cliente.save()
                        salva_auditoria(request, cliente, ACCION_MODIFICAR)
                        return ok_json()

                except Exception:
                    return bad_json(error=2)
            else:
                return bad_json(error=2)

        elif action == 'delete':
            try:
                cliente = Cliente.objects.get(pk=request.POST['id'])
                with transaction.atomic():
                    salva_auditoria(request, cliente, ACCION_ELIMINAR)
                    cliente.delete()
                    return ok_json()
            except Exception:
                return bad_json(error=3)

        elif action == 'resetear':
            try:
                cliente = Cliente.objects.get(pk=request.POST['id'])
                with transaction.atomic():
                    user = cliente.usuario
                    user.set_password(DEFAULT_PASSWORD)
                    user.save()
                    salva_auditoria(request, cliente, ACCION_MODIFICAR)
                    return ok_json()
            except Exception:
                return bad_json(error=3)

        return bad_json(error=0)

    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    data['title'] = u'Crear Cliente'
                    data['form'] = ClienteForm(initial={'fecha_nacimiento': datetime.now().date()})
                    return render_to_response("clientes/add.html", data)
                except Exception as ex:
                    pass

            elif action == 'edit':
                try:
                    data['title'] = 'Editar Cliente'
                    data['cliente'] = cliente = Cliente.objects.get(pk=request.GET['id'])
                    data['form'] = ClienteForm(initial={'tipo': cliente.tipo,
                                                        'identificacion': cliente.identificacion,
                                                        'nombre': cliente.nombre,
                                                        'domicilio': cliente.domicilio,
                                                        'fecha_nacimiento': cliente.fecha_nacimiento,
                                                        'email': cliente.email,
                                                        'telefono': cliente.telefono,
                                                        'celular': cliente.celular,
                                                        'usuario': cliente.usuario.username,
                                                        'ruc': cliente.ruc,
                                                        'razon_social': cliente.razon_social,
                                                        'representante_legal': cliente.representante_legal,
                                                        'tipo_cabello': cliente.tipo_cabello,
                                                        'tipo_piel': cliente.tipo_piel,
                                                        'caracteristicas_fisicas': cliente.caracteristicas_fisicas,
                                                        'alergias': cliente.alergias,
                                                        'oportunidades_servicios': cliente.oportunidades_servicios,
                                                        'foto': cliente.foto})
                    return render_to_response("clientes/edit.html", data)
                except Exception as ex:
                    pass

            elif action == 'delete':
                try:
                    data['title'] = 'Borrar Cliente'
                    data['cliente'] = Cliente.objects.get(pk=request.GET['id'])
                    return render_to_response("clientes/delete.html", data)
                except Exception as ex:
                    pass

            elif action == 'resetear':
                try:
                    data['title'] = u'Resetear clave del usuario'
                    data['cliente'] = Cliente.objects.get(pk=request.GET['id'])
                    return render_to_response("clientes/resetear.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        else:
            search = None
            tipo = None

            if 't' in request.GET and int(request.GET['t']) > 0:
                tipo = request.GET['t']

            if 's' in request.GET:
                search = request.GET['s']

            clientes = Cliente.objects.all().select_related('tipo_cabello', 'tipo_piel')
            if search:
                clientes = clientes.filter(Q(nombre__icontains=search) |
                                           Q(ruc__icontains=search) |
                                           Q(identificacion__icontains=search) |
                                           Q(email__icontains=search) |
                                           Q(usuario__username__icontains=search))
            if tipo:
                clientes = clientes.filter(tipo=tipo)

            paging = MiPaginador(clientes, 30)
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
            data['clientes'] = page.object_list
            data['tipoid'] = int(tipo) if tipo else ""
            return render_to_response("clientes/clientes.html", data)
