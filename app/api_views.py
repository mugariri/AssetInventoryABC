import json
from threading import Thread

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from app.apis import send_notification
from app.serializers import AssetCategorySerializer, AssetSerializer, DepartmentSerializer, SubDepartmentSerializer, \
    AssetTransferSerializer, ExternalCompanySerializer, AppAssetSerializer, ApplicationSerializer
from app.models import Asset, AssetCategory, Department, SubDepartment, AssetTransfer, ExternalCompany, Application
from core import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status


@api_view(['GET', 'POST'])
def asset_category_list(request):
    if request.method == 'GET':
        assetcategory = AssetCategory.objects.all()
        serializer = AssetCategorySerializer(assetcategory, many=True)
        # return JsonResponse(serializer.data, safe=False)
        return Response(serializer.data)

    elif request.method == 'POST':
        # data = JSONParser().parse(request)
        # serializer = AssetSerializer(data=data)
        serializer = AssetCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # return JsonResponse(serializer.data, status=201)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return JsonResponse(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def asset_category_detail(request, pk):
    try:
        asset_category = AssetCategory.objects.get(pk=pk)

    except AssetCategory.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = AssetCategorySerializer(asset_category)
        return JsonResponse(serializer.data)
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = AssetCategorySerializer(asset_category, data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)

        return JsonResponse(serializer.errors, status=400)
    elif request.method == 'DELETE':
        asset_category.delete()
        return HttpResponse(status=204)


@api_view(['GET', 'POST'])
def asset_list(request):
    if request.method == 'GET':
        asset = Asset.objects.all()
        serializer = AssetSerializer(asset, many=True)
        # return JsonResponse(serializer.data, safe=False)
        return Response(serializer.data)

    elif request.method == 'POST':
        # data = JSONParser().parse(request)
        # serializer = AssetSerializer(data=data)
        serializer = AssetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # return JsonResponse(serializer.data, status=201)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return JsonResponse(serializer.errors, status=400)


@api_view(['GET', 'POST'])
def asset_transfer_list(request):
    if request.method == 'GET':
        asset_transfer_list = AssetTransfer.objects.all()
        serializer = AssetTransferSerializer(asset_transfer_list, many=True)
        # return JsonResponse(serializer.data, safe=False)
        return Response(serializer.data)

    elif request.method == 'POST':
        # data = JSONParser().parse(request)
        # serializer = AssetSerializer(data=data)
        serializer = AssetTransferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # return JsonResponse(serializer.data, status=201)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return JsonResponse(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def asset_detail(request, serial_tag):
    try:
        asset = Asset.objects.get(serial_tag=serial_tag)

    except Asset.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = AssetSerializer(asset)
        return JsonResponse(serializer.data)
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = AssetSerializer(asset, data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)

        return JsonResponse(serializer.errors, status=400)
    elif request.method == 'DELETE':
        asset.delete()
        return HttpResponse(status=204)


@api_view(['GET', 'POST'])
def department_list(request):
    if request.method == 'GET':
        department = Department.objects.all()
        serializer = DepartmentSerializer(department, many=True)
        # return JsonResponse(serializer.data, safe=False)
        return Response(serializer.data)

    elif request.method == 'POST':
        # data = JSONParser().parse(request)
        # serializer = AssetSerializer(data=data)
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # return JsonResponse(serializer.data, status=201)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return JsonResponse(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def department_detail(request, pk):
    try:
        department = Department.objects.get(pk=pk)

    except Department.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = DepartmentSerializer(department)
        return JsonResponse(serializer.data)
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = DepartmentSerializer(department, data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)

        return JsonResponse(serializer.errors, status=400)
    elif request.method == 'DELETE':
        department.delete()
        return HttpResponse(status=204)


@api_view(['GET', 'POST'])
def sub_department_list(request):
    if request.method == 'GET':
        sub_department = SubDepartment.objects.all()
        serializer = SubDepartmentSerializer(sub_department, many=True)
        # return JsonResponse(serializer.data, safe=False)
        return Response(serializer.data)

    elif request.method == 'POST':
        # data = JSONParser().parse(request)
        # serializer = AssetSerializer(data=data)
        serializer = SubDepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # return JsonResponse(serializer.data, status=201)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return JsonResponse(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def sub_department_detail(request, pk):
    try:
        sub_department = SubDepartment.objects.get(pk=pk)

    except SubDepartment.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = DepartmentSerializer(sub_department)
        return JsonResponse(serializer.data)
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = SubDepartmentSerializer(sub_department, data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)

        return JsonResponse(serializer.errors, status=400)
    elif request.method == 'DELETE':
        sub_department.delete()
        return HttpResponse(status=204)


@api_view(['GET', 'PUT', 'DELETE'])
def external_company_details(request, pk):
    try:
        external_company = ExternalCompany.objects.get(pk=pk)

    except ExternalCompany.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = DepartmentSerializer(external_company)
        return JsonResponse(serializer.data)
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ExternalCompanySerializer(external_company, data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)

        return JsonResponse(serializer.errors, status=400)
    elif request.method == 'DELETE':
        external_company.delete()
        return HttpResponse(status=204)


@api_view(['GET', 'POST'])
def external_company_list(request):
    if request.method == 'GET':
        external_company = ExternalCompany.objects.all()
        serializer = ExternalCompanySerializer(external_company, many=True)
        # return JsonResponse(serializer.data, safe=False)
        return Response(serializer.data)

    elif request.method == 'POST':
        # data = JSONParser().parse(request)
        # serializer = AssetSerializer(data=data)
        serializer = ExternalCompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # return JsonResponse(serializer.data, status=201)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return JsonResponse(serializer.errors, status=400)


@api_view(['GET', 'POST'])
def asset_api_for_app(request):
    if request.method == 'GET':
        assets = Asset.objects.all()
        serializer = AppAssetSerializer(assets, many=True)
        # return JsonResponse(serializer.data, safe=False)
        return Response(serializer.data)

    elif request.method == 'POST':
        # data = JSONParser().parse(request)
        # serializer = AssetSerializer(data=data)
        serializer = AppAssetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # return JsonResponse(serializer.data, status=201)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return JsonResponse(serializer.errors, status=400)


@api_view(['GET', 'POST'])
def applications(request):
    if request.method == 'GET':
        apps = Application.objects.all()
        serializer = ApplicationSerializer(apps, many=True)
        # return JsonResponse(serializer.data, safe=False)
        return Response(serializer.data)

    elif request.method == 'POST':
        # data = JSONParser().parse(request)
        # serializer = AssetSerializer(data=data)
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # return JsonResponse(serializer.data, status=201)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return JsonResponse(serializer.errors, status=400)



@api_view(['GET', 'POST'])
def email_alert(request):
    if request.method == 'POST':
        json_object = json.dumps(request.data, indent=4)
        dictionary = {
            "subject": request.data['subject'],
            "message": request.data['message'],
            "receiver": request.data['email'],
        }
        Thread(target=send_notification, kwargs=dictionary).start()
        # send_notification(subject=request.data['subject'], message=request.data['message'], receiver=request.data['email'])

        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})