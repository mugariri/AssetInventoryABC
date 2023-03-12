from rest_framework import serializers

from app.models import AssetCategory, Asset, Department, SubDepartment, AssetTransfer, ExternalCompany, Application


class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = ['name']


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'




class AssetTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetTransfer
        fields = '__all__'


class ExternalCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalCompany
        fields = ['name', 'email', 'tel']


class AppAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['tag', 'serial_tag', 'active_directory_id', 'product_id', 'brand', 'model', 'date_of_manucturing' ]


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class SubDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubDepartment
        fields = '__all__'


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
