import datetime

from django.contrib import messages
from django.contrib.admin.forms import AdminPasswordChangeForm
from django.contrib.auth import update_session_auth_hash, login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import FormView, CreateView

from app.evaluate import validate_price, validate_ledger, validate_date, validate_allocation
from app.forms import EmployeeForm, BranchForm, AssetForm, EmployeeCreateForm
from app.models import Employee, AssetCategory, Department, Asset, AssetTransfer, SubDepartment, WorkBranch, \
    General_Ledger
from app.utilities import greetings


@login_required(login_url='abcassetsmanager:login')
def index(request):
    template = 'app/hardware_request_list.html'
    form = BranchForm()
    aform = AssetForm()
    if request.method == 'POST':
        if aform.is_valid():
            print(aform.cleaned_data['tag'])
    context = {
        'form': form,
        'aform': aform
    }

    return render(request, template, context)


@login_required(login_url="abcassetsmanager:login")
def assets_manager(request):
    template = 'app/side.html'
    if request.method == 'POST':
        category = request.POST.get('category')
        asset_tag = request.POST.get('asset_tag')
        serial_number = request.POST.get('serial_number')
        colour = request.POST.get('colour')
        brand = request.POST.get('brand')
        spec = request.POST.get('spec')
        model = request.POST.get('model')
        date_purchased = request.POST.get('purchased')
        date_received = request.POST.get('received')
        currency = request.POST.get('currency')
        price = request.POST.get('dollars')
        cents = request.POST.get('cents')
        gl = request.POST.get('gl')
        user = request.POST.get('allocated')
        doc = request.POST.get('document')
        print(doc)

        if len(asset_tag) > 6 and len(serial_number) > 5:
            try:
                category = AssetCategory.objects.get(name=category)
                Asset.objects.get(tag=asset_tag)
                messages.warning(request, "Asset Already Exists")
            except Asset.DoesNotExist:
                if serial_number is not None or asset_tag != '':

                    asset = Asset.objects.create(
                        category=category, tag=asset_tag,
                        serial_tag=serial_number,
                        colour=colour,
                        brand=brand,
                        model=model,
                        specs=spec,
                        registered_by=request.user,
                        currency=currency,
                        price=validate_price(price=price, cents=cents),
                        general_ledger_account=validate_ledger(gl),
                        purchase_date=validate_date(date_purchased),
                        received_date=validate_date(date_received),
                        allocated_user=validate_allocation(user),
                        purchase_request_document=doc
                    )

                    asset.save()
                    messages.success(request, "Asset Created Successifully")
                else:
                    messages.warning(request, "Input tag and serial")
            except AssetCategory.DoesNotExist:
                messages.success(request, "Asset Category Not Found")
            except BaseException as e:
                print("failed to create asset ", e)
                messages.success(request, e)
        else:
            messages.warning(request, "Asset Tag and SerialNumber are required")

    context = {
        'categories': AssetCategory.objects.all(),
        'greetings': greetings,
        "arrivals": AssetTransfer.objects.filter(
            acknowledged_by_receiver=False,
            new_custodian=request.user,
            is_approved=True
        ),
        'aw': AssetTransfer.objects.filter(is_approved=False, approved_by=request.user)[:5],
        'users': User.objects.all(),
    }
    return render(request, template, context)


def user_login(request):
    template = 'app/login.html'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        auth_response = {}
        # user = authenticate(
        #      request,
        #      username=username,
        #      password=password,
        #      response=auth_response,
        # )
        user = User.objects.get(username=username)
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
            return redirect('abcassetsmanager:user_update')

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

                return redirect('abcassetsmanager:login')
    context = {

    }

    return render(request, template, context)


class SignUpView(CreateView):
    template_name = 'app/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('abcassetsmanager:dashboard')

    def form_valid(self, form):
        valid = super().form_valid(form)
        login(self.request, self.object)
        return valid


def validate_username(request):
    """Check username availability"""
    username = request.GET.get('username', None)
    response = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(response)


def register_user(request):
    template = 'app/register.html'

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        user.set_password(password)
        user.save()
        created_user = User.objects.get(username=username)
        profile = Employee.objects.create(user=created_user)
        profile.save()
        print("Profile Created Successfully")
        return redirect('abcassetsmanager:index')
    else:

        pass

    return render(request, template)


def employee_update(request):
    template = 'app/emp.html'
    departments = Department.objects.all()
    users = User.objects.all()
    context = {
        'depts': departments,
        'users': users
    }
    return render(request, template, context)


def user_logout(request):
    logout(request)
    return redirect('abcassetsmanager:login')


def user_update(request):
    Employee.objects.get_or_create(user=request.user)
    template = 'app/profile_update.html'
    if not request.user.employee.updated:
        if request.method == 'POST':
            department = request.POST.get('department')
            sub_department = request.POST.get('sub_department')
            line_manager = request.POST.get('line_manager')
            work_address = request.POST.get('work_address')
            branch = request.POST.get('branch')
            extension = request.POST.get('extension')
            phone_number = request.POST.get('phone')
            # phone_number(phone_number)

            try:
                department = Department.objects.get(name=department)
                line_manager = User.objects.get(username=line_manager)
                branch = WorkBranch.objects.get(name=branch)
                employee = Employee.objects.get(user=request.user)
                employee.department = department
                employee.line_manager = line_manager
                employee.work_address = work_address
                employee.extension = extension
                employee.updated = True
                employee.mobile_number = phone_number
                employee.branch = branch
                employee.save()
                return redirect('abcassetsmanager:my_assets')
            except Department.DoesNotExist:
                print("Department does not exist")
                messages.warning(request, "Department does not exist")
            except WorkBranch.DoesNotExist:
                print("WorkBranch does not exist")
                messages.warning(request, "WorkBranch does not exist")
            except User.DoesNotExist:
                print("User does not exist")
                messages.warning(request, "Line Manager does not exist")
            except SubDepartment.DoesNotExist:
                print("SubDepartment does not exist")
                messages.warning(request, "SubDepartment does not exist")
            except Employee.DoesNotExist:
                print("Employee does not exist")
                messages.warning(request, "Employee does not exist")
            except BaseException as e:
                print(e)
                messages.warning(request, 'An error occured')
    else:
        return redirect('abcassetsmanager:my_assets')
    context = {
        'departments': Department.objects.all(),
        'sub_departments': SubDepartment.objects.all(),
        'branches': WorkBranch.objects.all(),
        'users': User.objects.all(),
    }
    return render(request, template, context)


def detailed_data_report(request):
    template = 'app/data_report.html'
    context = {
        'assets': Asset.objects.all(),
    }
    return render(request, template, context=context)
