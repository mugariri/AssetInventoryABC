from datetime import date
import datetime
from app.detail_views import department_list
from app.models import Department, HardwareRequisition, WorkBranch, Asset
from django.shortcuts import render, redirect
from django.contrib import messages
from app.utilities import greetings
from django.db.models import Q

def assets_report_for_branch(request, branch_id):
    template = 'app/assets_report_for_branch.html'

    try:
        branch = WorkBranch.objects.get(id=branch_id)
        assets = Asset.objects.filter(custodian_user__employee__branch=branch)
        print(assets)



    except WorkBranch.DoesNotExist:
        print("Branch not existant")
    
    context = {
        'greetings': greetings,
        'assets': Asset.objects.filter(custodian_user__employee__branch=branch),
        'branch': WorkBranch.objects.get(id=branch_id)
    }

    return render(request, template, context)


def hardware_request_report_for_branch(request, branch_id):
    template = 'app/requests_report_for_branch.html'
    start_date = datetime.date(2022, 9, 1)
    end_date = datetime.date(2022, 10, 30)
    try:
        start_date = datetime.date(2022, 9, 1)
        end_date = datetime.date(2022, 10, 30)
        branch = WorkBranch.objects.get(id=branch_id)
        reqs =HardwareRequisition.objects.filter(date_logged__range=(start_date, end_date), requisitioner__employee__branch=branch)
        
    except WorkBranch.DoesNotExist:
        print("Branch not existant")
    
    context = {
        'requesitions' :HardwareRequisition.objects.filter(date_logged__range=(start_date, end_date), requisitioner__employee__branch=branch),
        'greetings': greetings,
        'reqs': HardwareRequisition.objects.all(),
        'branch': WorkBranch.objects.get(id=branch_id),
        
    }


    return render(request, template, context=context)



def asset_transfer_report_for_branch(request, branch_id):
    template = 'app/transfers_report_for_branch.html'
    start_date = datetime.date(2022, 9, 1)
    end_date = datetime.date(2022, 10, 30)
    try:
        start_date = datetime.date(2022, 9, 1)
        end_date = datetime.date(2022, 10, 30)
        branch = WorkBranch.objects.get(id=branch_id)
        reqs =HardwareRequisition.objects.filter(date_logged__range=(start_date, end_date), requisitioner__employee__branch=branch)
        
    except WorkBranch.DoesNotExist:
        print("Branch not existant")
    
    context = {
        'requesitions' :HardwareRequisition.objects.filter(date_logged__range=(start_date, end_date), requisitioner__employee__branch=branch),
        'greetings': greetings,
        'reqs': HardwareRequisition.objects.all(),
        'branch': WorkBranch.objects.get(id=branch_id),
        
    }


    return render(request, template, context=context)




def generate_report_for_department(request):
    template = 'app/generate_dept_report.html'
    if request.method == "POST":
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        restriction = request.POST.get('restriction')
        branch_id = request.POST.get('branch')
        print(from_date)
        print(to_date)
        try:
            if restriction == "assets":
                return redirect("abcassetsmanager:assets_report_for_department", dept_id=branch_id)
            elif restriction == 'transfers':
                print('transfers')
            elif restriction == 'requests':
                print("requests")
                return redirect('abcassetsmanager:hardware_request_report_for_branch', branch_id=branch_id)
            elif restriction == None:
                messages.warning(request, "404 Restriction")
        except WorkBranch.DoesNotExist:
            messages.warning(request, "Branch not found")
            print("Branch not existant")
        
    context = {
        'depts': Department.objects.all(),
        'greetings': greetings
    }

    return render(request, template, context)





def generate_report(request):
    template = 'app/report_filters.html'
    if request.method == "POST":
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        restriction = request.POST.get('restriction')
        branch_id = request.POST.get('branch')
        print(to_date, " to ",from_date)
        print(to_date.split('-'))
        try:
            if restriction == "assets":
                return redirect("abcassetsmanager:assets_report_for_branch", branch_id=branch_id)
            elif restriction == 'transfers':
                print('transfers')
            elif restriction == 'requests':
                return redirect('abcassetsmanager:hardware_request_report_for_branch', branch_id=branch_id)
            elif restriction == None:
                messages.warning(request, "404 Restriction")
        except Department.DoesNotExist:
            messages.warning(request, "Branch not found")
            print("Branch not existant")
        
    context = {
        'branchs': WorkBranch.objects.all(),
        'greetings': greetings
    }

    return render(request, template, context)


def assets_report_for_department(request, dept_id):
    template = 'app/assets_report_for_branch.html'

    try:
        department = Department.objects.get(id=dept_id)
        assets = Asset.objects.filter(custodian_user__employee__department=department)
        print(assets)



    except WorkBranch.DoesNotExist:
        print("Branch not existant")
    
    context = {
        'greetings': greetings,
        'assets': Asset.objects.filter(custodian_user__employee__department=department),
        'dept': Department.objects.get(id=dept_id)
    }

    return render(request, template, context)