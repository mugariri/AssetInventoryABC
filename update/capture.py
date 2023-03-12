import subprocess as sb
from time import sleep
import requests

import time

def notify_by_email(email, tag, serial_tag):
    subject = "ASSET REGISTRATION NOTIFICATION"
    message = f"""
    <h4>An asset with the details below has been registered in your custody</h4><br>
    <b>ASSET TAG<b> : {tag}<br>
    <b>SERIAL TAG<b> : {serial_tag}<br>
    Ignore this if you confirm
    Contact IT if information is incorrect
    """
    email_url = 'http://10.106.60.5:8000/api/email_alert/'
    email = email + "@bancabc.co.zw"
    try:
        r = requests.post(email_url, data={'email': email, 'subject': subject,'message': message})
    except BaseException as e:
        print(e)


def get_and_post_data():
    output = sb.getoutput("systeminfo")
    serial_tag = sb.getoutput("wmic bios get serialnumber").split('\n')[2].rstrip()
    username = sb.getoutput("whoami").split("\\")[1]
    hostname = output.split("\n")[1].split(":")[1].strip()
    product_id = output.split("\n")[9].split(":")[1].strip()
    manufacturer = output.split("\n")[12].split(":")[1].strip()
    model = output.split("\n")[13].split(":")[1].strip()
    year = output.split("\n")[17].split(":")[1].strip().split(",")[1].strip().split("/")[2]
    day = output.split("\n")[17].split(":")[1].strip().split(",")[1].strip().split("/")[1]
    month = output.split("\n")[17].split(":")[1].strip().split(",")[1].strip().split("/")[0]

    host_ip = "10.106.60.5:8000"
    tag = input("Enter Asset Tag: ")
    tag_2 = input("Confirm Asset Tag:")
    prompt = """Please respond according to type of device\n
          1 : LAPTOP\n

          2 : DESKTOP\n"""
    category = input(f"{prompt} Enter Category: ")

    url = f"http://{host_ip}/api/asset_list"

    params = {
        "active_directory_id": f'{hostname}',
        "tag": f"{tag}",
        "username": f"{username}",
        "serial_tag": f'{serial_tag}',
        "brand": f'{manufacturer}',
        'model': f'{model}',
        'product_id': f'{product_id}',
        "category": category,
        "registered_by": 3,
    }
    notify_by_email(email=username, tag=tag, serial_tag=serial_tag)
    if tag == tag_2 and tag is not None:
        try:
            r = requests.post(url=url, data=params)
            print("posted")
            time.sleep(5)
        except BaseException as exception:
            print(exception)
            sleep(10)

    else:
        print("Tag Does Not Match")
        time.sleep(10)
        exit(1)

if __name__ == '__main__':
    get_and_post_data()
    #notify_by_email(email="dmugariri", tag="abctest", serial_tag="serial tag")