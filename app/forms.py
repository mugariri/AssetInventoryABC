from django import forms

from app.models import Employee, WorkBranch, Asset


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['title', 'mobile_number', 'department', 'sub_department']

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class BranchForm(forms.ModelForm):
    class Meta:
        model = WorkBranch
        fields = ['name', 'code', 'location', 'default_extension']

    def __init__(self, *args, **kwargs):
        super(BranchForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class EmployeeCreateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_number', 'department', 'mobile_number']

    def __init__(self, *args, **kwargs):
        super(EmployeeCreateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
