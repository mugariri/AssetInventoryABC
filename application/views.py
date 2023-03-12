from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from application.models import Computer


def user_login(request):
    template = 'application/login.html'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        auth_response = {}
        user = authenticate(
            request,
            username=username,
            password=password,
            response=auth_response,
        )
        # user = User.objects.get(username=username)
        if user:
            # Login the user
            login(request, user)
            post_login_callback = None
            # RUn post login
            from bancapis.abc.auth import import_name
            try:
                post_login_callback = import_name('ABC_AUTH_POST_LOGIN_CALLBACK')
            except BaseException:
                pass

            if post_login_callback:
                post_login_callback(request)
            # messages.success(request, 'login successful.')
            return redirect('application:deploy')

        else:
            # Use auth response to generate error message

            if auth_response.get('status_known', False):
                if auth_response.get('not_found'):
                    message = 'Reference account not found'
                    messages.success(request, f'{message}')
                elif auth_response.get('is_locked', False):
                    message = 'Reference account currently locked out'
                    messages.success(request, f'{message}')
                else:
                    message = 'Incorrect password'
                    messages.success(request, f'{message}')
            else:
                message = 'Incorrect username or password'
                messages.success(request, f'{message}')
                # raise ValueError("Login failed:{}".format(message))

                return redirect('application:login')
    context = {

    }

    return render(request, template, context)


@login_required(login_url='application:login')
def deploy(request):
    template = 'application/deploy.html'

    if request.method == 'POST':
        tag = request.POST.get('tag')
        custodian = request.POST.get('custodian')
        computer = request.POST.get('computer')
        old_computer_name = request.POST.get('old_computer')
        print(tag, computer, custodian, old_computer_name)
        try:
            Computer.objects.get(abc_asset_tag=tag)
            messages.warning(request, "Deployment Failed : ALREADY EXISTS")

        except Computer.DoesNotExist:
            Computer.objects.create(
                new_active_directory_name=computer.upper(),
                custodian=custodian.upper(),
                configured_by=request.user,
                abc_asset_tag=tag.upper(),
            ).save()
            print("Asset Created Succesifully")
            messages.success(request, "Deployment Registed")
        except BaseException as exception:
            print(exception)
    context = {
        'deployments': Computer.objects.all(),
        'total': Computer.objects.all(),
        'mine': Computer.objects.filter(configured_by=request.user),
        'uncleared': Computer.objects.filter(cleared=False),
        'cleared': Computer.objects.filter(cleared=True),
    }
    return render(request, template, context)


@login_required(login_url='application:login')
def update(request, id):
    template = 'application/update.html'
    dep = Computer.objects.get(id=id)
    if request.method == 'POST':
        tag = request.POST.get('tag')
        custodian = request.POST.get('custodian')
        computer = request.POST.get('computer')
        old_computer_name = request.POST.get('old_computer')
        print(tag, computer, custodian, old_computer_name)
        try:
            dep.new_active_directory_name = computer
            dep.custodian = custodian
            dep.configured_by = request.user
            dep.abc_asset_tag = tag
            dep.save()
            print("Asset Created Succesifully")
            messages.success(request, "Deployment Updated")
        except BaseException as exception:
            print(exception)
    context = {
        'deployments': Computer.objects.all(),
        'total': Computer.objects.all(),
        'mine': Computer.objects.filter(configured_by=request.user),
        'uncleared': Computer.objects.filter(cleared=False),
        'cleared': Computer.objects.filter(cleared=True),
        'dep': Computer.objects.get(id=id),
    }
    return render(request, template, context)


@login_required(login_url='application:login')
def uncleared(request):
    template = 'application/uncleared.html'
    context = {
        'deployments': Computer.objects.all(),
        'total': Computer.objects.all(),
        'mine': Computer.objects.filter(configured_by=request.user),
        'uncleared': Computer.objects.filter(cleared=False),
        'cleared': Computer.objects.filter(cleared=True),
    }
    return render(request, template, context)


@login_required(login_url='application:login')
def mine(request):
    template = 'application/mine.html'
    print(Computer.objects.filter(configured_by=request.user))
    context = {
        'deployments': Computer.objects.all(),
        'total': Computer.objects.all(),
        'mine': Computer.objects.filter(configured_by=request.user),
        'uncleared': Computer.objects.filter(cleared=False),
        'cleared': Computer.objects.filter(cleared=True),
    }
    return render(request, template, context)


@login_required(login_url='application:login')
def clear(request, id):
    template = "application/clear.html"
    try:
        dep = Computer.objects.get(id=id)
        if not dep.cleared:
            if request.method == "POST":
                clear = request.POST.get('clear')
                print(clear)
                if clear is not None:
                    try:
                        dep.cleared = True
                        dep.cleared_by = request.user
                        dep.save()
                        messages.success(request, "Device Cleared ")
                    except BaseException as exception:
                        messages.warning(request, exception)

            else:
                return redirect('application:notification_page', message="ALREADY CLEARED")
    except Computer.DoesNotExist:
        return redirect('application:notification_page', message="DEPLOYMENT 404")
    except BaseException as exception:
        print(exception)
    context = {
        'deployments': Computer.objects.all(),
        'total': Computer.objects.all(),
        'mine': Computer.objects.filter(configured_by=request.user),
        'uncleared': Computer.objects.filter(cleared=False),
        'cleared': Computer.objects.filter(cleared=True),
        'dep': Computer.objects.get(id=id),
    }
    return render(request, template, context)


@login_required(login_url='application:login')
def cleared(request):
    template = "application/cleared.html"

    context = {
        'deployments': Computer.objects.all(),
        'total': Computer.objects.all(),
        'mine': Computer.objects.filter(configured_by=request.user),
        'uncleared': Computer.objects.filter(cleared=False),
        'cleared': Computer.objects.filter(cleared=True),
    }
    return render(request, template, context)


@login_required(login_url='application:login')
def deployments(request):
    template = "application/deployments.html"

    context = {
        'deployments': Computer.objects.all(),
        'total': Computer.objects.all(),
        'mine': Computer.objects.filter(configured_by=request.user),
        'uncleared': Computer.objects.filter(cleared=False),
        'cleared': Computer.objects.filter(cleared=True),
    }
    return render(request, template, context)


@login_required(login_url='application:login')
def deployment(request, id):
    template = 'application/deployment.html'
    try:
        dep = Computer.objects.get(id=id)
    except BaseException as exception:
        print(exception)
    context = {
        'deployments': Computer.objects.all(),
        'total': Computer.objects.all(),
        'mine': Computer.objects.filter(configured_by=request.user),
        'uncleared': Computer.objects.filter(cleared=False),
        'cleared': Computer.objects.filter(cleared=True),
        'dep': Computer.objects.get(id=id),

    }
    return render(request, template, context)


@login_required(login_url='application:login')
def notification(request, message):
    template = 'application/notification.html'
    context = {

    }
    return render(request, template, context)


def user_logout(request):
    logout(request)
    return redirect('application:login')
