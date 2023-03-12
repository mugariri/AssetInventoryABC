from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from app.models import Employee, Asset, AssetCategory, SubDepartment, Department, AssetTransfer, TransferType, \
    ReasonForTransfer, ExternalCompany, AssetAssignment, HardwareRequisition
from app.tools import notify_user, unlock_asset, generate_ref, calculate_lifespan, acknowledge_custody, \
    send_for_repairs, assign_asset_to_usernames, make_procurer, make_deployer, make_manager
from app.utilities import greetings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from app.notifications import notify_pending_approval, notify_asset_transfer, notify_hardware_request, \
    in_manager_notify_hardware_request, head_of_tech_notify_hardware_request, line_manager_notify_hardware_request, \
    notify_external_asset_transfer


# on_repairs = AssetTransfer.objects.filter(is_approved=True, type=TransferType.objects.get(name="External"),
#                                           returned=False)


@login_required(login_url='abcassetsmanager:login')
def department_list(request):
    template = ''
    return render(request, template)


@login_required(login_url='abcassetsmanager:login')
def department_detail(request, department_id):
    template = ''
    department = Department.objects.get(id=department_id)
    return render(request, template)


@login_required(login_url='abcassetsmanager:login')
def sub_department_detail(request, sub_department_id):
    template = ''
    sub_department = SubDepartment.objects.get(id=sub_department_id)
    context = {
        'sub_department': sub_department,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template)


@login_required(login_url='abcassetsmanager:login')
def category_detail(request, category_id):
    template = ''
    category = AssetCategory.objects.get(id=category_id)
    context = {
        'category': category,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template)


# def

@login_required(login_url='abcassetsmanager:login')
def asset_list(request):
    template = 'app/asset_list.html'
    assets = Asset.objects.all()
    assign_asset_to_usernames()
    context = {
        'assets': assets,
        'greetings': greetings,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


def printable(request):
    template = 'app/printable.html'
    return render(request, template)


def printing(request):
    template = 'app/print.html'
    return render(request, template)


def print_hardware_request_document(request, id):
    template = 'app/print_hardware_request.html'
    print(id)
    hr = HardwareRequisition.objects.get(id=id)
    print(hr.asset)
    context = {
        'hr': hr
    }
    return render(request, template, context=context)

@login_required(login_url='abcassetsmanager:login')
def asset_transfer(request, id):
    template = 'app/asset_transfer.html'

    try:
        transfer = AssetTransfer.objects.get(id=id)
        asset = Asset.objects.get(tag=transfer.asset.tag)
        sender = request.user
        internal_transfer = TransferType.objects.get(name="Internal")
        recipient = transfer.new_custodian

        if request.method == 'POST':
            approved = request.POST.get('approved')
            if approved is not None:
                if transfer.type == internal_transfer:
                    transfer.is_approved = True
                    recipient.employee.assigned_assets.add(asset)
                    asset.assigned_to = recipient
                    asset.is_assigned = True
                    recipient.employee.assigned_assets.add(asset)
                    transfer.save()
                    notify_user(request, transfer, "notify_user.txt")
                    asset.save()
                    notify_asset_transfer(transfer_id=id)
                    messages.success(request, "Transfer Approved")
                else:
                    transfer.is_approved = True
                    transfer.asset.on_repairs = True
                    transfer.asset.custodian_user = None
                    transfer.save()
                    messages.success(request, "Transfer Approved")

            else:
                print(transfer.reference)
                print("Not approved")
                messages.warning(request, "Transfer Not Actioned")
    except Asset.DoesNotExist:
        print("Asset DoesNotExist")
    except User.DoesNotExist:
        print("User DoesNotExist")
    except AssetTransfer.DoesNotExist:
        print("Asset TransferDoesNotExist")
    except BaseException as e:
        print(e)
    context = {
        'greetings': greetings,
        'transfer': transfer,
        'approved': transfer.is_approved,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        # 'on_repairs': on_repairs,
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def transfer_multiple_assets(request):
    template = 'app/multiple.html'
    assets = Asset.objects.all()
    types = TransferType.objects.all()
    users = User.objects.all()
    reasons = ReasonForTransfer.objects.all()

    if request.method == 'POST':
        assets = request.POST.getlist('assets')
        username = request.POST.get('user')
        type = request.POST.get('type')
        approver = request.POST.get('approver')
        # reason = request.POST.get('reason')
        reason_for_transfer = request.POST.get('reason_for_transfer')
        # recipient = User.objects.get(username=username)
        print(reason_for_transfer)
        if len(assets) >= 1:
            for id in assets:
                try:
                    # reason = ReasonForTransfer.objects.get(name=reason)
                    recipient = User.objects.get(username=username)
                    asset = Asset.objects.get(id=id)
                    if asset.locked:
                        print("Asset is locked by other transfer")
                        messages.warning(request, "Asset is locked by other transfer")
                    else:
                        try:
                            if reason_for_transfer is not None:
                                transfer = AssetTransfer.objects.create(
                                    reference=generate_ref(),
                                    type=TransferType.objects.get(name="Internal"),
                                    asset=Asset.objects.get(id=id),
                                    being_moved_by=request.user,
                                    approved_by=User.objects.get(username=approver),
                                    new_custodian=User.objects.get(username=recipient),
                                    src_department=request.user.employee.department,
                                    dest_department=recipient.employee.department,
                                    # reason=ReasonForTransfer.objects.get(name=reason),
                                    reason_for_transfer=reason_for_transfer,
                                )
                                transfer.multiple_assets.add(asset)
                                transfer.save()
                                notify_pending_approval(transfer_id=transfer.id)
                                asset.save()
                                notify_user(request, transfer, "approval_request.txt")
                                print("Transfer initiated")
                                messages.success(request, "Transfer Initiated")
                            else:
                                messages.warning(request, "reason for transfer not specified")
                        except ReasonForTransfer.DoesNotExist:
                            messages.warning(request, "Reason For Transfer")
                        except User.DoesNotExist:
                            messages.warning(request, "User Does Not Exist")
                        except BaseException as e:
                            print(e)

                except ReasonForTransfer.DoesNotExist:
                    print("ReasonForTransfer not found")
                    messages.warning(request, "Reason for transfer not found")
                except User.DoesNotExist:
                    messages.warning(request, "User not found")
                    print("recipient not found in system")
                except BaseException as e:

                    print(e)

        else:
            messages.warning(request, "**no assets selected**")
        assets = Asset.objects.filter(locked=False)

    context = {
        'greetings': greetings,
        # 'reasons': ReasonForTransfer.objects.all(),
        'types': TransferType.objects.all(),
        'assets': Asset.objects.filter(locked=False),
        'users': User.objects.all(),
        'managers': User.objects.filter(username=request.user.employee.line_manager.username),
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:3],
        # 'on_repairs': on_repairs,
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def await_approval(request):
    template = 'app/awaiting_approval.html'
    awaiting_approval = AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)

    context = {
        'greetings': greetings,
        'awaiting_approval': awaiting_approval,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        # 'on_repairs': on_repairs,
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def user_detail(request, user_id):
    template = ''
    user = User.objects.get(id=user_id)
    employee = Employee.objects.get(user=user)
    context = {
        'employee': employee,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        # 'on_repairs': on_repairs,
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template)


# @cache_page(60*15)
@login_required(login_url='abcassetsmanager:login')
def transfer_list(request):
    template = 'app/transfer_list.html'

    transfers = AssetTransfer.objects.all()

    context = {
        'greetings': greetings,
        'transfers': transfers,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        # 'on_repairs': on_repairs,
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def dashboard(request):
    template = 'app/dashboard.html'

    transfers = AssetTransfer.objects.all()
    assets = Asset.objects.all()
    print(request.get_host())
    context = {
        'transfers': transfers,
        'assets': assets,
        'greetings': greetings,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        # 'on_repairs': on_repairs,
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def acknowledge(request, id):
    global transfer
    template = 'app/acknowledge.html'

    try:
        transfer = AssetTransfer.objects.get(id=id)
        assets = Asset.objects.all()
        if transfer.type.name == "Internal":
            if request.method == 'POST':
                acknowledge = request.POST.get('acknowledge')
                if acknowledge is not None:
                    transfer.acknowledged_by_receiver = True
                    transfer.received = True
                    unlock_asset(transfer.asset)
                    acknowledge_custody(request.user, transfer.asset)
                    transfer.new_custodian.employee.assigned_assets.add(transfer.asset)
                    transfer.save()
                    messages.success(request, "Asset Received Successfully")
                else:
                    messages.warning(request, "Not Actioned")
        elif transfer.type.name == "External":
            if request.method == 'POST':
                acknowledge = request.POST.get('acknowledge')
                if acknowledge is not None:
                    print(acknowledge)
                    unlock_asset(transfer.asset)
                    transfer.on_repairs = False
                    transfer.returned = True
                    transfer.save()
                    messages.success(request, "Asset Returned Successfully")
                else:
                    messages.warning(request, "Not Actioned")
    except AssetTransfer.DoesNotExist:
        print("Asset transfer does not exist")
    except BaseException as e:
        print(e)

    context = {
        'transfer': transfer,
        'assets': assets,
        'greetings': greetings,
        'can_acknowledge': transfer.new_custodian,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        # 'on_repairs': on_repairs,
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def user_maintenance_page(request):
    template = 'app/user_maintenance_page.html'
    user = request.user
    employee = Employee.objects.get(user=user)
    departments = Department.objects.all()
    context = {
        'user': user,
        'greetings': greetings,
        'subdepartments': SubDepartment.objects.all(),
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        # 'on_repairs': on_repairs,
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def create_category(request):
    template = 'app/create_category.html'
    if request.method == 'POST':
        name = request.POST.get('name')
        dept = request.POST.get('dept')
        sub_dept = request.POST.get('sub_dept')

        try:
            department = Department.objects.get(name=dept)
            sub_department = SubDepartment.objects.get(name=sub_dept)
            try:
                AssetCategory.objects.get(name=name)
                print("Already created")
            except AssetCategory.DoesNotExist:
                AssetCategory.objects.create(name=name, department_in_charge=department,
                                             sub_department=sub_department)
                print("Category Created")
        except SubDepartment.DoesNotExist:
            print("No SubDepartment")
        except Department.DoesNotExist:
            print("No Department")
        except BaseException as e:
            print(e)
    context = {
        'sub_depts': SubDepartment.objects.all(),
        'depts': Department.objects.all(),
        'greetings': greetings,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        # 'on_repairs': on_repairs,
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def asset_details(request, asset_id):
    template = 'app/asset_details.html'
    try:
        asset = get_object_or_404(Asset, id=asset_id)

    except Asset.DoesNotExist:
        print("Asset does not exist")
    except BaseException as exception:
        print(exception)
    context = {
        'greetings': greetings,
        'asset': get_object_or_404(Asset, id=asset_id),
        'age': calculate_lifespan(asset.date_created.date()),
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        # 'on_repairs': on_repairs,
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def transfer_details(request, transfer_id):
    template = 'app/transfer_details.html'

    transfer = get_object_or_404(AssetTransfer, id=transfer_id)
    context = {
        'greetings': greetings,
        'transfer': transfer,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def my_assets(request):
    template = 'app/my_assets.html'
    my_assigned_assets = Asset.objects.filter(assigned_to=request.user, on_repairs=False)
    # print(request.session._session_key)

    # print(request.session['last_activity'])

    context = {
        'greetings': greetings,
        'assets': my_assigned_assets,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def create_department(request):
    template = 'app/create_department.html'
    if request.method == 'POST':
        name = request.POST.get('name')
        head = request.POST.get('head')

        if len(name) > 6:
            try:
                head = User.objects.get(id=head)
                Department.objects.get(name=name)
                messages.warning(request, 'Department already exists')
            except Department.DoesNotExist:
                Department.objects.create(name=name, head=head)
                messages.success(request, 'Department created successfully')

            except User.DoesNotExist:
                messages.warning(request, "Select Head of Department")
        else:
            messages.warning(request, 'Name does not meet requirements')
    context = {
        'greetings': greetings,
        'users': User.objects.all(),
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:url')
def unacknowledged(request):
    template = 'app/arrivals.html'
    arrivals = AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                            is_approved=True)

    context = {
        'greetings': greetings,
        'arrivals': arrivals,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
    }
    return render(request, template, context=context)


@login_required(login_url='abcassetsmanager:login')
def transfer_my_asset(request):
    template = 'app/transfer_my_asset.html'
    assets = Asset.objects.all()
    types = TransferType.objects.all()
    users = User.objects.all()
    reasons = ReasonForTransfer.objects.all()
    if request.method == 'POST':
        assets = request.POST.getlist('assets')
        username = request.POST.get('user')
        type = request.POST.get('type')
        approver = request.POST.get('approver')
        # reason = request.POST.get('reason')
        reason_for_transfer = request.POST.get('reason_for_transfer')
        # recipient = User.objects.get(username=username)
        print(reason_for_transfer)
        if len(assets) >= 1:
            for id in assets:
                try:
                    # reason = ReasonForTransfer.objects.get(name=reason)
                    recipient = User.objects.get(username=username)
                    asset = Asset.objects.get(id=id)
                    if asset.locked:
                        print("Asset is locked by other transfer")
                        messages.warning(request, "Asset is locked by other transfer")
                    else:
                        try:
                            transfer = AssetTransfer.objects.create(
                                reference=generate_ref(),
                                type=TransferType.objects.get(name="Internal"),
                                asset=Asset.objects.get(id=id),
                                being_moved_by=request.user,
                                approved_by=User.objects.get(username=approver),
                                new_custodian=User.objects.get(username=recipient),
                                src_department=request.user.employee.department,
                                dest_department=recipient.employee.department,
                                # reason=ReasonForTransfer.objects.get(name=reason),
                                reason_for_transfer=reason_for_transfer,
                            )
                            transfer.multiple_assets.add(asset)
                            transfer.save()
                            notify_pending_approval(transfer_id=transfer.id)
                            asset.save()
                            notify_user(request, transfer, "approval_request.txt")
                            print("Transfer initiated")
                            messages.success(request, "Transfer Initiated")
                        except ReasonForTransfer.DoesNotExist:
                            messages.warning(request, "Reason For Transfer")
                        except User.DoesNotExist:
                            messages.warning(request, "User Does Not Exist")
                        except BaseException as e:
                            print(e)

                except ReasonForTransfer.DoesNotExist:
                    print("ReasonForTransfer not found")
                    messages.warning(request, "Reason for transfer not found")
                except User.DoesNotExist:
                    messages.warning(request, "User not found")
                    print("recipient not found in system")
                except BaseException as e:

                    print(e)

        else:
            messages.warning(request, "**no assets selected**")
        assets = Asset.objects.filter(locked=False)

    context = {
        'greetings': greetings,
        # 'reasons': ReasonForTransfer.objects.all(),
        'types': TransferType.objects.all(),
        'assets': Asset.objects.filter(assigned_to=request.user, locked=False),
        'users': User.objects.all(),
        'managers': User.objects.filter(username=request.user.employee.line_manager.username),
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:3],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def external_transfers(request):
    template = 'app/external_transfers.html'
    if request.method == 'POST':
        assets = request.POST.getlist('selected')
        company_name = request.POST.get('company')
        type = request.POST.get('type')
        approver = request.POST.get('approver')
        reason = request.POST.get('reason_for_transfer')
        print(company_name)
        for asset_tag in assets:
            try:

                company = ExternalCompany.objects.get(name=company_name)
                print(company)
                asset = Asset.objects.get(tag=asset_tag)
                approved_by = User.objects.get(username=approver)

                if asset.locked:
                    print("Asset is locked by other transfer")
                    messages.warning("Asset is locked by other transfer")
                else:
                    try:
                        check = AssetTransfer.objects.get(
                            reference=f'{type}:{request.user.username}:{asset_tag}:{asset.serial_tag}:{company}:1')
                        print("reference exists")
                    except AssetTransfer.DoesNotExist:
                        transfer = AssetTransfer.objects.create(
                            reference=generate_ref(),
                            type=TransferType.objects.get(name="External"),
                            asset=Asset.objects.get(tag=asset_tag),
                            being_moved_by=request.user,
                            approved_by=User.objects.get(username=approver),
                            new_custodian=None,
                            src_department=request.user.employee.department,
                            external_company=company,
                            reason_for_transfer=reason,
                        )
                        transfer.multiple_assets.add(asset)
                        transfer.external_company.assets_sent.add(transfer.asset)
                        transfer.save()
                        asset.locked = True
                        asset.save()
                        asset = Asset.objects.get(tag=asset_tag)
                        asset.on_repairs = True
                        notify_external_asset_transfer(transfer.id)
                        messages.success(request, "Transfer Sent For Authorisation")
                        asset.save()
            except ReasonForTransfer.DoesNotExist:
                print("ReasonForTransfer not found")
                messages.success(request, "Reason For Transfer not found")
            except User.DoesNotExist:
                print("auth user not found in system")
            except ExternalCompany.DoesNotExist as e:
                print("external does not exist", e)
                messages.success(request, "Company does not exist")
            except BaseException as e:
                print(e)

        assets = Asset.objects.filter(locked=False)

    context = {
        'greetings': greetings,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        'assets': Asset.objects.filter(locked=False, on_repairs=False),
        'reasons': ReasonForTransfer.objects.all(),
        'companies': ExternalCompany.objects.all(),
        'users': User.objects.all(),
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def return_asset(request, id):
    global transfer
    template = 'app/acknowledge.html'
    try:
        transfer = AssetTransfer.objects.get(id=id)
        if transfer.type == TransferType.objects.get(name="External"):
            if request.method == 'POST':
                acknowledge = request.POST.get('acknowledge')
                print(acknowledge)
                if acknowledge is not None:
                    # transfer.acknowledged_by_receiver = True
                    transfer.returned = True
                    unlock_asset(transfer.asset)
                    acknowledge_custody(request.user, transfer.asset)
                    transfer.asset.on_repairs = False
                    transfer.save()
        else:
            return redirect("abcassetsmanager:acknowledge", id=transfer.id)
    except AssetTransfer.DoesNotExist:
        print("Asset transfer does not exist")
    except BaseException as exception:
        print("Exception ", exception)

    context = {
        'transfer': transfer,
        'greetings': greetings,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        'external': TransferType.objects.get(name="External"),
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


def assets_on_repairs(request):
    template = 'app/on_repairs.html'
    transfers = AssetTransfer.objects.filter(is_approved=True, type=TransferType.objects.get(name="External"),
                                             returned=False)
    context = {
        'greetings': greetings,
        'transfers': transfers,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def assign_asset(request):
    template = 'app/assign_asset.html'
    hardware_requests = HardwareRequisition.objects.all()
    if request.method == 'POST':
        assignee_id = request.POST.get('assignee')
        assets = request.POST.getlist('asset')
        hr = request.POST.get('request')
        try:
            resolved_request = HardwareRequisition.objects.get(id=hr)
            for asset_id in assets:
                try:

                    asset = Asset.objects.get(id=asset_id)
                    assignee = User.objects.get(id=assignee_id)
                    asset.assigned_to = assignee
                    assignment = AssetAssignment.objects.create(asset=asset, assignee=assignee, assigner=request.user)
                    assignment.save()
                    if resolved_request is not None:
                        assignment.req = resolved_request
                        resolved_request.purcharsed = True
                    resolved_request.asset = asset
                    resolved_request.save()
                    asset.save()
                    messages.success(request, 'Asset Assigned Successifully')
                except HardwareRequisition.DoesNotExist:
                    print("hardware does not exist")
        except User.DoesNotExist:
            print("user does not exist")
            messages.warning(request, 'User not found')
        except Asset.DoesNotExist:
            print("asset not found")
            messages.warning(request, 'Asset not found')
        except BaseException as e:
            print(e)
    context = {
        'assets': Asset.objects.filter(assigned_to=None),
        'greetings': greetings,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True),
        'users': User.objects.all(),
        'hardware_requests': HardwareRequisition.objects.filter(authorizer_accepted=True,
                                                                infrastructure_manager_accepted=True,
                                                                head_of_technology_services_accepted=True,
                                                                purcharsed=False)

    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
@permission_required(perm='employee.can_give_rights', login_url='abcassetsmanager:my_assets')
def give_permissions(request):
    template = 'app/permissions.html'
    if request.method == 'POST':
        procurer = request.POST.get('procurer')
        deployer = request.POST.get('deployer')
        manager = request.POST.get('manager')
        users = request.POST.getlist('users')
        try:
            if procurer is not None:
                for user in users:
                    make_procurer(user)
                    messages.success(request, 'Procurer Rights Done')

            if deployer is not None:
                for user in users:
                    make_deployer(user)
                    messages.success(request, 'Deployer Rights Done')
            if manager is not None:
                for user in users:
                    make_manager(user)
                    messages.success(request, 'Manager Rights Done')
            messages.success(request, "User Rights Assigned")
        except BaseException as e:
            print(e)
    context = {
        'assets': Asset.objects.filter(assigned_to=None),
        'greetings': greetings,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True),
        'users': User.objects.all()
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def hardware_request(request):
    template = 'app/hardware_request.html'

    if request.method == 'POST':
        reason = request.POST.get('reason')
        head = request.POST.get('head')
        justification = request.POST.get('justification')
        category = request.POST.get('category')
        replace = request.POST.get('replace')
        designation = request.POST.get('designation')

        try:
            authorized_by = User.objects.get(username=head)
            category = AssetCategory.objects.get(name=category)
            if len(str(justification)) is not None:
                print(justification)
                hardware_request = HardwareRequisition.objects.create(
                    requisitioner=request.user,
                    authorized_by=authorized_by,
                    reason_for_request=reason,
                    designation=designation,
                    justification_for_purchase=justification,
                    department=request.user.employee.department,
                    device_requested=category
                )
                hardware_request.line_manager = request.user.employee.line_manager
                hardware_request.save()
                line_manager_notify_hardware_request(hardware_request.id)
                #

                messages.success(request, "Request Sent For Authorization")
                if replace is not None:
                    hardware_request.replacement = True
                    hardware_request.save()
            else:
                messages.success(request, "a detailed justification required")


        except User.DoesNotExist:
            messages.warning(request, "Select Authorizer")
        except AssetCategory.DoesNotExist:
            messages.warning(request, "Select Asset Category")
        except BaseException as e:
            messages.warning(request, e)
            print(e)
    context = {
        'categories': AssetCategory.objects.all(),
        'greetings': greetings,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True),
        'heads': User.objects.filter(employee__is_head_of_dept=True)
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def pending_line_manager(request):
    template = 'app/pending_line_manager.html'
    requests = HardwareRequisition.objects.all()
    context = {
        'reqs': HardwareRequisition.objects.all(),
        'greetings': greetings,
        'hardware_request': hardware_request,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True),
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def line_manager_approve(request, id):
    template = 'app/line_manage_approval.html'
    requests = HardwareRequisition.objects.all().filter(line_manager_approved=False, line_manager_rejected=False)

    if request.method == 'POST':
        approve = request.POST.get('approve')
        revoke = request.POST.get('revoke')
        line_manager_justification = request.POST.get('justification')
        try:

            req = HardwareRequisition.objects.get(id=id)
            if line_manager_justification == '':
                messages.warning(request, 'Provide Brief Justification')
            if approve is not None and line_manager_justification != "":
                print("approved")
                messages.success(request, "Approved Successfully")
                req.line_manager_approved = True
                req.line_manager_comment = line_manager_justification
                req.line_manager = request.user
                req.save()
                notify_hardware_request(req.id)
            if revoke is not None and line_manager_justification != "":
                messages.success(request, "Revoked Successfully")
                req.line_manager_rejected = True
                req.line_manager = request.user
                req.line_manager_comment = line_manager_justification
                req.save()
                print("Revoked Successfully")

            if approve is not None and revoke is not None:
                messages.warning(request, 'Please Select A Single Action')
        except BaseException as exception:
            messages.warning(request, exception)

    context = {
        'req': HardwareRequisition.objects.get(id=id),
        'reqs': HardwareRequisition.objects.all(),
        'greetings': greetings,
        'hardware_request': hardware_request,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True),
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def approve_hardware_request(request, id):
    template = 'app/hod_approval.html'
    if request.user.employee.is_head_of_dept:
        try:
            hardware_request = HardwareRequisition.objects.get(id=id)

            if request.method == 'POST':
                approve = request.POST.get('approve')
                close = request.POST.get('revoke')
                authorizer_justification = request.POST.get('justification')
                print(approve, close, authorizer_justification)
                if authorizer_justification != "":
                    if approve is not None and close is not None:
                        messages.warning(request, "Can't approve and reject simultaneously'")
                    else:
                        if approve is not None and request.user == hardware_request.authorized_by:
                            hardware_request.authorizer_accepted = True
                            hardware_request.department_decided = True
                            hardware_request.authorizer_justification = authorizer_justification
                            hardware_request.save()
                            in_manager_notify_hardware_request(hardware_request.id)
                            messages.success(request, "Hardware Request Approved")
                        if close is not None and request.user == hardware_request.authorized_by:
                            hardware_request.authorizer_rejected = True
                            hardware_request.authorizer_justification = authorizer_justification
                            hardware_request.department_decided = True
                            hardware_request.save()
                            messages.success(request, "Hardware Request Revoked")
                        if request.user != hardware_request.authorized_by:
                            messages.success(request, "Permission Denied")
                        hardware_request.save()
                else:
                    messages.warning(request, "Kindly Add Justification")
        except HardwareRequisition.DoesNotExist:
            print("request not found")
        except BaseException as e:
            print(e)
    else:

        messages.warning(request, "Access Denied")
        return render(request, template, {
            'greetings': greetings
        })
    context = {
        'req': HardwareRequisition.objects.get(id=id),
        'greetings': greetings,
        'hardware_request': hardware_request,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True),
        'heads': User.objects.filter(employee__is_head_of_dept=True),
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def pending_requests(request):
    template = 'app/pending_hardware.html'
    context = {
        'greetings': greetings,
        'requesitions': HardwareRequisition.objects.filter(authorizer_accepted=False, authorized_by=request.user,
                                                           authorizer_rejected=False, line_manager_approved=True),
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True),
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def all_hardware_requests(request):
    template = 'app/hardware_request_list.html'

    context = {
        'greetings': greetings,
        'requesitions': HardwareRequisition.objects.all(),
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True),
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def infrastructure_manager_pendings(request):
    template = 'app/inmanager_hardware_request_list.html'

    context = {
        'greetings': greetings,
        'reqs': HardwareRequisition.objects.filter(authorizer_accepted=True, infrastructure_manager_accepted=False,
                                                   infrastructure_manager_rejected=False),
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True),
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def infrastructure_manager_approve(request, id):
    template = 'app/in_manager_approve_hardware.html'
    if request.user.employee.IN_manager == True:
        try:
            hardware_request = HardwareRequisition.objects.get(id=id)
            if request.method == 'POST':
                justification = request.POST.get('justification')
                approve = request.POST.get('approve')
                close = request.POST.get('revoke')
                if close is not None and approve is not None:
                    messages.success(request, "Can't Approve and Revoke Simultaneously")
                elif close is None and approve is None:
                    messages.warning(request, "No Action Selected")
                elif close is not None:
                    hardware_request.infrastructure_manager_reason_for_action = justification
                    hardware_request.infrastructure_manager = request.user
                    hardware_request.infrastructure_manager_rejected = True
                    hardware_request.infrastructure_decided = True
                    hardware_request.save()
                    messages.success(request, "Hardware Request Revoked")
                elif approve is not None:
                    hardware_request.infrastructure_manager_reason_for_action = justification
                    hardware_request.infrastructure_manager = request.user
                    hardware_request.infrastructure_manager_accepted = True
                    hardware_request.infrastructure_decided = True
                    hardware_request.save()
                    head_of_tech_notify_hardware_request(hardware_request.id)
                    messages.success(request, "Hardware Request Approved")
                else:
                    messages.warning(request, "Error")

        except HardwareRequisition.DoesNotExist:
            print("Request not found")
        except BaseException as e:
            print(e)
    else:
        messages.warning(request, "Your have no permissions")
    context = {
        'req': HardwareRequisition.objects.get(id=id),
        'greetings': greetings,
        'hardware_request': HardwareRequisition.objects.get(id=id),
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True),
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def head_of_tech_services_pendings(request):
    template = 'app/head_of_tech_services_pendings.html'

    context = {
        'greetings': greetings,
        'reqs': HardwareRequisition.objects.filter(authorizer_accepted=True, infrastructure_manager_accepted=True,
                                                   head_of_technology_services_accepted=False,
                                                   head_of_technology_services_rejected=False),
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True),
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def head_of_tech_services_approve(request, id):
    # template = 'app/head_of_tech_approve_hardware.html'
    template = 'app/hod_tech.html'
    req = None
    try:
        req = HardwareRequisition.objects.get(id=id)
        if request.method == 'POST':
            approve = request.POST.get('approve')
            revoke = request.POST.get('revoke')
            justification = request.POST.get('justification')
            if justification != "":
                if req is not None:
                    if revoke is not None and approve is not None:
                        messages.warning(request, "Cant Approve and Revoke Simultaneously")
                    elif approve is not None:
                        req.head_of_technology_services_accepted = True
                        req.head_of_technology_services_decided = True
                        req.head_of_technology_services = request.user
                        req.head_of_technology_services_reason_for_action = justification
                        req.save()
                        messages.success(request, "Request Approved Successfully")

                    elif revoke is not None:
                        req.head_of_technology_services = request.user
                        req.head_of_technology_services_rejected = True
                        req.head_of_technology_services_decided = True
                        req.head_of_technology_services_reason_for_action = justification
                        req.save()
                        messages.success(request, "Request Revoked Successifully")
                    else:
                        messages.warning(request, "No Action Taken")
            else:
                messages.warning(request, "Please provide justification")


    except HardwareRequisition.DoesNotExist:
        print("HardwareRequisition does not exist")
    except BaseException as e:
        print(e)
    context = {
        'req': req,
        'greetings': greetings,
        'hardware_request': HardwareRequisition.objects.get(id=id),
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],

        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True),
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def successiful_request(request):
    template = 'app/successiful_request.html'
    context = {
        'greetings': greetings,
        'requesitions': HardwareRequisition.objects.filter(authorizer_accepted=True,
                                                           infrastructure_manager_accepted=True,
                                                           head_of_technology_services_accepted=True, purcharsed=False),
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True),
    }
    return render(request, template, context)


@login_required(login_url='abcassetsmanager:login')
def hardware_request_details(request, id):
    template = 'app/hardware_request_details.html'
    hardware_request = None
    try:
        hardware_request = get_object_or_404(HardwareRequisition, id=id)

    except HardwareRequisition.DoesNotExist:
        messages.warning(request, "Hardware Request 404")

    except BaseException as e:
        messages.warning(request, e)

    context = {
        'greetings': greetings,
        'req': hardware_request
    }
    return render(request, template, context)


def create_subdepartment(request, department_id):
    template = 'app/create_department.html'
    dept = None
    try:
        dept = Department.objects.get(id=department_id)

    except Department.DoesNotExist:
        print("Department does not exist")

    except BaseException as e:
        print(e)

    return render(request, template, )


@login_required(login_url='abcassetsmanager:login')
def approve_transfer(request, id):
    template = 'app/approve_transfer.html'
    transfer = AssetTransfer.objects.get(id=id)
    try:
        transfer = AssetTransfer.objects.get(id=id)
        asset = Asset.objects.get(tag=transfer.asset.tag)
        sender = request.user
        internal_transfer = TransferType.objects.get(name="Internal")
        external_transfer = TransferType.objects.get(name="External")
        recipient = transfer.new_custodian

        if request.method == 'POST':

            approved = request.POST.get('approve')
            narration = request.POST.get('narration')
            if approved is not None:
                if transfer.type == internal_transfer:
                    transfer.is_approved = True
                    recipient.employee.assigned_assets.add(asset)
                    asset.assigned_to = recipient
                    asset.is_assigned = True
                    recipient.employee.assigned_assets.add(asset)
                    transfer.narration = narration
                    transfer.save()
                    notify_user(request, transfer, "notify_user.txt")
                    asset.save()
                    notify_asset_transfer(transfer_id=id)
                    messages.success(request, "Transfer Approved")
                elif transfer.type == external_transfer:
                    print("External Transfer")
                    transfer.is_approved = True
                    transfer.narration = narration
                    transfer.save()
                    asset.save()
                    messages.success(request, "Transfer Approved")
                else:
                    transfer.is_approved = True
                    transfer.asset.on_repairs = True
                    transfer.asset.custodian_user = None
                    transfer.save()
                    messages.success(request, "Transfer Approved")

            else:
                print(transfer.reference)
                print("Not approved")
                messages.warning(request, "Transfer Not Actioned")
    except Asset.DoesNotExist:
        print("Asset DoesNotExist")
    except User.DoesNotExist:
        print("User DoesNotExist")
    except AssetTransfer.DoesNotExist:
        print("Asset TransferDoesNotExist")
    except BaseException as e:
        print(e)
    context = {
        'greetings': greetings,
        'transfer': transfer,
        'approved': transfer.is_approved,
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        "arrivals": AssetTransfer.objects.filter(acknowledged_by_receiver=False, new_custodian=request.user,
                                                 is_approved=True)
    }
    return render(request, template, context)
