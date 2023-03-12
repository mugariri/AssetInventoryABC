# Import the xlrd module
import warnings
from ftplib import FTP

import xlrd
import pandas as pd

from app.models import Asset, AssetCategory, WorkBranch
from app.capture import post_asset


def extract_data_from_xls() -> None:
    dataframe1 = pd.read_excel('\\\\10.105.200.75\\updated softwares\\a\\register.xlsx')
    # print(dataframe1['Asset Tag'][0])
    for index, row in dataframe1.iterrows():
        # print(row["Asset Tag"], row['Serial No'])

        params = {
            "tag": f"{row['Serial No']}",
            "username": f"{row['Allocated User']}",
            "serial_tag": f'{row["Asset Tag"]}',
            # "date_of_manufacturing": f"{year}-{month}-{day}"
        }
        print(params)
        try:
            # Asset.objects.create(tag=row["Asset Tag"], serial_tag=row['Serial No'])
            post_asset(params=params, url='http://127.0.0.1:8000/api/asset_list')

        except BaseException as e:
            print(e)
        pass


def use_existing_template():
    warnings.simplefilter(action='ignore', category=UserWarning)
    # file = '\\\\10.105.200.75\\updated softwares\\ASSET REGISTER\\IT ASSET REGISTER FILE.xlsm'
    file = 'excel files/IT ASSET REGISTER.xlsx'
    df = pd.read_excel(file)
    # print(df['User'], df['AssetTag No'], df['Asset Type'])
    category = None
    for index, row in df.iterrows():
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
                Asset.objects.create(tag=row['AssetTag No'], serial_tag=row['Printer / Laptop '], username=row['User'],
                                     category=category, location=WorkBranch.objects.get(name=row['Location']))
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
                Asset.objects.create(tag=row['AssetTag No'], serial_tag=row['Desktop Serial Numbers '],
                                     username=row['User']).save()
            except BaseException as e:
                print(e)

    return None


class UploadData:
    def __init__(self):

        pass

    def extract_data_from_xls(self) -> None:
        dataframe1 = pd.read_excel('\\\\10.105.200.75\\updated softwares\\a\\register.xlsx')
        # print(dataframe1['Asset Tag'][0])
        for index, row in dataframe1.iterrows():
            # print(row["Asset Tag"], row['Serial No'])

            params = {
                "tag": f"{row['Serial No']}",
                "username": f"{row['Allocated User']}",
                "serial_tag": f'{row["Asset Tag"]}',
                # "date_of_manufacturing": f"{year}-{month}-{day}",
                "location": f"{WorkBranch.objects.get(name=row['Location'])}"
            }
            try:
                # Asset.objects.create(tag=row["Asset Tag"], serial_tag=row['Serial No'])
                post_asset(params=params, url='http://127.0.0.1:8000/api/asset_list')

            except BaseException as e:
                print(e)
            pass

    def use_existing_template(self):
        warnings.simplefilter(action='ignore', category=UserWarning)
        # file = '\\\\10.105.200.75\\updated softwares\\ASSET REGISTER\\IT ASSET REGISTER FILE.xlsm'
        file = 'excel files/IT ASSET REGISTER.xlsx'
        df = pd.read_excel(file)
        # print(df['User'], df['AssetTag No'], df['Asset Type'])
        category = None
        for index, row in df.iterrows():
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
                    Asset.objects.create(tag=row['AssetTag No'], serial_tag=row['Printer / Laptop '],
                                         username=row['User'], category=category,
                                         location=WorkBranch.objects.get(name=row['Location']))
                    # WorkBranch.objects.create(name=row['Location']).save()
                except BaseException as e:
                    print(e)
            if str(row['Asset Type']) == "Laptop":
                category = AssetCategory.objects.get(name='Laptop')
                try:
                    Asset.objects.create(tag=row['AssetTag No'], serial_tag=row['Printer / Laptop '],
                                         username=row['User'],
                                         category=category)
                    WorkBranch.objects.create(name=row['Location']).save()
                except BaseException as e:
                    print(e)
            if str(row['Asset Type']) == 'Desktop':
                category = AssetCategory.objects.get(name='Desktop CPU')
                try:
                    Asset.objects.create(tag=row['AssetTag No'], serial_tag=row['Desktop Serial Numbers '],
                                         username=row['User']).save()
                except BaseException as e:
                    print(e)

        return None
