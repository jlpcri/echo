import pysftp

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render

from echo.apps.core import messages
from echo.apps.settings.forms import ServerForm, ServerPreprodForm
from echo.apps.settings.models import Server, PreprodServer


def user_is_superuser(user):
    return user.is_superuser


@user_passes_test(user_is_superuser)
def index(request):
    if request.method == 'GET':
        return redirect('settings:servers', permanent=True)
    return HttpResponseNotFound()


@user_passes_test(user_is_superuser)
def servers(request):
    if request.method == 'GET':
        return render(request, "settings/servers.html",
                      {'servers': Server.objects.all().order_by("name"), 'server_form': ServerForm()})
    elif request.method == 'POST':
        if "add_server" in request.POST:
            form = ServerForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                address = form.cleaned_data['address']
                account = form.cleaned_data['account']
                server = Server(name=name, address=address, account=account)
                try:
                    server.full_clean()
                    server.save()
                    messages.success(request, "Added server to list")
                    return redirect("settings:servers")
                except ValidationError as e:
                    print e.message_dict
                    if 'name' in e.message_dict:
                        messages.danger(request, e.message_dict.get('name')[0])
                    elif 'address' in e.message_dict:
                        messages.danger(request, e.message_dict.get('address')[0])
                    return render(request, "settings/servers.html",
                                  {'servers': Server.objects.all().order_by("name"), 'server_form': form})
            messages.danger(request, "Unable to add server to list")
            return render(request, "settings/servers.html",
                          {'servers': Server.objects.all().order_by("name"), 'server_form': form})
        elif "delete_server" in request.POST:
            sid = request.POST.get('sid', "")
            if sid:
                server = get_object_or_404(Server, pk=sid)
                server.delete()
                messages.success(request, "Server \"{0}\" has been deleted".format(server.name))
                return redirect("settings:servers")
            messages.danger(request, "Unable to delete server")
            return render(request, "settings/servers.html",
                          {'servers': Server.objects.all().order_by("name"), 'server_form': ServerForm()})
        elif "test_connection" in request.POST:
            sid = request.POST.get('sid', "")
            if sid:
                server = get_object_or_404(Server, pk=sid)
                try:
                    with pysftp.Connection(server.address, username=str(server.account),
                                           private_key=settings.PRIVATE_KEY) as conn:
                        conn.chdir('/')
                except IOError:
                    messages.danger(request, "Unable to connect to server \"{0}\"".format(server.name))
                    return redirect("settings:servers")
                except pysftp.ConnectionException:
                    messages.danger(request, "Connection error to server \"{0}\"".format(server.name))
                    return redirect("settings:servers")
                except pysftp.CredentialException:
                    messages.danger(request, "Credentials error to server \"{0}\"".format(server.name))
                    return redirect("settings:servers")
                except pysftp.AuthenticationException:
                    messages.danger(request, "Authentication error to server \"{0}\"".format(server.name))
                    return redirect("settings:servers")
                except pysftp.SSHException:
                    messages.danger(request, "SSH error to server \"{0}\"".format(server.name))
                    return redirect("settings:servers")
                messages.success(request, "Successful connection to server \"{0}\"".format(server.name))
                return redirect("settings:servers")
        elif "update_active" in request.POST:
            sid = request.POST.get('sid', "")
            servers = Server.objects.all()
            for server_active in servers:
                if server_active:
                    server_active.active = False
                    server_active.save()

            server = get_object_or_404(Server, pk=sid)
            server.active = True
            server.save()
            return redirect("settings:servers")
    return HttpResponseNotFound()


@user_passes_test(user_is_superuser)
def users(request):
    """View for user management dashboard"""
    if request.method == 'GET':
        return render(request, "settings/users.html", {'users': User.objects.all().order_by('username')})
    elif request.method == 'POST':
        if "update_user" in request.POST:
            uid = request.POST.get('uid', "")
            if uid:
                user = get_object_or_404(User, pk=uid)
                user.is_active = request.POST.get('is_active', False)
                user.is_staff = request.POST.get('is_staff', False)
                user.usersettings.creative_services = request.POST.get('is_cs', False)
                user.usersettings.project_manager = request.POST.get('is_pm', False)
                user.is_superuser = request.POST.get('is_superuser', False)
                user.save()
                user.usersettings.save()
                messages.success(request, "Updated user \"{0}\"".format(user.username))
                return redirect("settings:users")
            messages.danger(request, "Unable to delete user")
            return render(request, "settings/users.html", {'users': User.objects.all().order_by("username")})
        elif "delete_user" in request.POST:
            uid = request.POST.get('uid', "")
            if uid:
                user = get_object_or_404(User, pk=uid)
                user.delete()
                messages.success(request, "User \"{0}\" has been deleted".format(user.username))
                return redirect("settings:users")
            messages.danger(request, "Unable to delete user")
            return render(request, "settings/users.html", {'users': User.objects.all().order_by("username")})
    return HttpResponseNotFound()


@user_passes_test(user_is_superuser)
def servers_preprod(request):
    if request.method == 'GET':
        return render(request, "settings/servers_preprod.html",
                      {'servers_preprod': PreprodServer.objects.all().order_by("name"),
                       # Application type default: Producer-1, NativeVxml-2
                       'server_form_preprod': ServerPreprodForm(initial={'application_type': '1'})})
    elif request.method == 'POST':
        if "add_server_preprod" in request.POST:
            form = ServerPreprodForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                address = form.cleaned_data['address']
                account = form.cleaned_data['account']
                application_type = form.cleaned_data['application_type']
                server = PreprodServer(name=name,
                                       address=address,
                                       account=account,
                                       application_type=application_type
                                       )
                try:
                    server.full_clean()
                    server.save()
                    messages.success(request, "Added preprod server to list")
                    return redirect("settings:servers_preprod")
                except ValidationError as e:
                    if 'name' in e.message_dict:
                        messages.danger(request, e.message_dict.get('name')[0])
                    elif 'address' in e.message_dict:
                        messages.danger(request, e.message_dict.get('address')[0])
                    return render(request, "settings/servers_preprod.html",
                                  {'servers_preprod': PreprodServer.objects.all().order_by("name"),
                                   'server_form_preprod': form})
            messages.danger(request, "Unable to add server to list")
            return render(request, "settings/servers_preprod.html",
                          {'servers_preprod': PreprodServer.objects.all().order_by("name"),
                           'server_form_preprod': form})
        elif "delete_server_preprod" in request.POST:
            sid = request.POST.get('sid', "")
            if sid:
                server = get_object_or_404(PreprodServer, pk=sid)
                server.delete()
                messages.success(request, "Preprod Server \"{0}\" has been deleted".format(server.name))
                return redirect("settings:servers_preprod")
            messages.danger(request, "Unable to delete preprod server")
            return render(request, "settings/servers_preprod.html",
                          {'servers_preprod': PreprodServer.objects.all().order_by("name"),
                           'server_form_preprod': ServerPreprodForm()
                          })
        elif "test_connection_preprod" in request.POST:
            sid = request.POST.get('sid', "")
            if sid:
                server = get_object_or_404(PreprodServer, pk=sid)
                try:
                    with pysftp.Connection(server.address, username=str(server.account),
                                           private_key=settings.PRIVATE_KEY) as conn:
                        conn.chdir('/')
                except IOError:
                    messages.danger(request, "Unable to connect to preprod server \"{0}\"".format(server.name))
                    return redirect("settings:servers_preprod")
                except pysftp.ConnectionException:
                    messages.danger(request, "Connection error to preprod server \"{0}\"".format(server.name))
                    return redirect("settings:servers_preprod")
                except pysftp.CredentialException:
                    messages.danger(request, "Credentials error to preprod server \"{0}\"".format(server.name))
                    return redirect("settings:servers_preprod")
                except pysftp.AuthenticationException:
                    messages.danger(request, "Authentication error to preprod server \"{0}\"".format(server.name))
                    return redirect("settings:servers_preprod")
                except pysftp.SSHException:
                    messages.danger(request, "SSH error to preprod server \"{0}\"".format(server.name))
                    return redirect("settings:servers_preprod")
                messages.success(request, "Connecting to preprod server \"{0}\"".format(server.name))
                return redirect("settings:servers_preprod")
    return HttpResponseNotFound()