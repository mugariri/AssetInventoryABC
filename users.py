from django.contrib.auth.models import User
import pandas as pd

def create_users():
    dataframe1 = pd.read_excel('users.xlsx')
    print(dataframe1.columns)
   
    # print(dataframe1['Asset Tag'][0])
    for index,  row in dataframe1.iterrows() :
        # print((row["Username"]))
        try:
            print(row["Username"], row["First Name"], row["Last Name"], row["E-Mail Address"])
            User.objects.get_or_create(username=row["Username"], first_name=row["First Name"], last_name=row["Last Name"])
            pass
        except BaseException as e:
            print(e)


create_users()
