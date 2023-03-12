from django.contrib.auth.models import User
import pandas as pd


def create_users():
    dataframe1 = pd.read_excel('users.xlsx')
    print(dataframe1.columns)

    # print(dataframe1['Asset Tag'][0])
    for index, row in dataframe1.iterrows():
        # print((row["Username"]))
        try:
            User.objects.get_or_create(username=row["Username"], first_name=row["First Name"],
                                       last_name=row["Last Name"])
            pass
        except BaseException as e:
            print(e)


def create_user_from_names():
    dataframe1 = pd.read_excel('users.xlsx')
    print(dataframe1.columns)

    # print(dataframe1['Asset Tag'][0])
    for index, row in dataframe1.iterrows():
        if len(row["Username"]) < 2 and row["Last Name"] == "Kiosk":
            username = str(row["First Name"]).lower(),
            # print()
            try:
                User.objects.get_or_create(username=username[0], first_name=row["First Name"],
                                           last_name=row["Last Name"])
                print(username, 'created')
            except BaseException as e:
                print(e)
        # User.objects.create(username=row["Username"], first_name=row["First Name"], last_name=row["Last Name"])
        pass
