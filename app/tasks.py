# from core.celery import app
import warnings

import pandas as pd
from celery import current_app as app

from app.models import WorkBranch, AssetCategory, Asset


@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)


@app.task
def use_existing_template():
    warnings.simplefilter(action='ignore', category=UserWarning)
    # file = '\\\\10.105.200.75\\updated softwares\\ASSET REGISTER\\IT ASSET REGISTER FILE.xlsm'
    file = 'excel files/IT ASSET REGISTER.xlsx'
    df = pd.read_excel(file)
    # print(df['User'], df['AssetTag No'], df['Asset Type'])
    category = None
    for index , row in df.iterrows():
        if str(row['Asset Type']) == "nan":
            # print("not existant", row['AssetTag No'])
            try:
                if str(row['Location']) != "nan":
                    WorkBranch.objects.get_or_create(name=row['Location'])
            except BaseException as e:
                print(e)
        if str(row['Asset Type']) == 'Printer':
            category = AssetCategory.objects.get(name='Printer')
            # print(str(row['Printer / Laptop '])+ '  :  '+ str(row['AssetTag No'])+ " : " + str(row['User']) + " : " +str(row['Asset Type']))
            try:
                Asset.objects.create(tag=row['AssetTag No'], serial_tag =row['Printer / Laptop '], username=row['User'], category=category, location=WorkBranch.objects.get(name=row['Location']))
                # WorkBranch.objects.create(name=row['Location']).save()
            except BaseException as e:
                print(e)
        if str(row['Asset Type']) == "Laptop":
            category = AssetCategory.objects.get(name='Laptop')
            try:
                Asset.objects.create(tag=row['AssetTag No'], serial_tag=row['Printer / Laptop '], username=row['User'],
                                 category=category)
                WorkBranch.objects.create(name=row['Location']).save()
            except BaseException as e:
                print(e)
        if str(row['Asset Type']) == 'Desktop':
            category = AssetCategory.objects.get(name='Desktop CPU')
            try:
                Asset.objects.create(tag=row['AssetTag No'], serial_tag=row['Desktop Serial Numbers '], username=row['User']).save()
            except BaseException as e:
                print(e)

    return None
