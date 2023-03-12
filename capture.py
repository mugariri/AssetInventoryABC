import subprocess as sb
from threading import Thread
from time import sleep
import requests

data = None
import time

serial_tag = sb.getoutput("wmic bios get serialnumber").split('\n')[2].rstrip()
# url = "http://10.106.60.5:8000/api/asset_list"
# url = "http://127.0.0.1:8000/api/asset_list"
protocol = "http://"
ip = '10.106.60.5'
debug_ip = "127.0.0.1"
port = 8000
asset_list_link = '/api/asset_list'

url = f'{protocol}{ip}:{port}{asset_list_link}'


def get_asset_tag():
    tag = input("Enter Asset Tag: ")
    tag_2 = input("Confirm Asset Tag:")
    if tag == tag_2:
        if tag.startswith("ABC") or tag.startswith("abc"):
            if len(tag) < 6:
                print("Asset Tag is too short")
                sleep(5)
                exit(1)
            else:
                return tag.upper()
        else:
            print("Asset Naming conventions not followed")
            exit(1)
    else:
        print("asset tag does not match")
        sleep(10)
        exit(1)
        return None


def delete_asset_from_system(serial_tag):
    get_asset_url = f'{protocol}{ip}:{port}/api/asset_detail/{serial_tag}/'
    update_asset = requests.delete(get_asset_url)
    return update_asset


def post_asset(url, params):
    global r
    try:
        r = requests.post(url=url, data=params)
        if r.status_code == 201:
            print("Successiful Post")
        elif r.status_code == 400:
            print(r.json(), " message")
            if r.json()['serial_tag'][0] == "asset with this serial tag already exists.":
                try:
                    if delete_asset_from_system(serial_tag).status_code == 204:
                        r = requests.post(url=url, data=params)
                        if r.status_code == 201:
                            print("Asset Updated")
                        else:
                            print("failed to update")
                    else:
                        print("failed to fetch")


                except BaseException as e:
                    print(e)
    except BaseException as e:
        print(e)
    return requests.post(url=url, data=params)


def get_category():
    prompt = """Please respond according to type of device\n
          1 : LAPTOP\n
          2 : DESKTOP\n"""
    category = input(f"{prompt} Enter Category: ")

    if category == "1":
        return category
    elif category == "2":
        return category

    else:

        print("Catgory does not exit")
        exit(1)
        return None


def get_data(tag, category):
    output = sb.getoutput("systeminfo")
    serial_tag = sb.getoutput("wmic bios get serialnumber").split('\n')[2].rstrip()
    username = sb.getoutput("whoami").split("\\")[1]
    hostname = output.split("\n")[1].split(":")[1].strip()
    product_id = output.split("\n")[9].split(":")[1].strip()
    manufacturer = output.split("\n")[12].split(":")[1].strip()
    model = output.split("\n")[13].split(":")[1].strip()
    date_manufactured = output.split("\n")[17].split(":")[1].strip().split(",")[1].strip()

    params = {
        "active_directory_id": f'{hostname}',
        "tag": f"{tag}",
        "username": f"{username}",
        "serial_tag": f'{serial_tag}',
        "brand": f'{manufacturer}',
        'model': f'{model}',
        'product_id': f'{product_id}',
        "category": category,
        "registered_by": 519,
        "bios_date": date_manufactured,
        # "date_of_manufacturing": f"{year}-{month}-{day}"
    }
    return params


def do():
    post_asset(params=get_data(get_asset_tag(), get_category()), url=url)
    data = "Helloo"


def rest():
    # print('sleeping')
    sleep(15)


if __name__ == '__main__':
    # Thread(target=rest).start()
    threads = []
    t = Thread(target=do)
    th = Thread(target=rest)
    threads.append(t)
    threads.append(th)


    for thread in threads:
        thread.start()
        thread.join()
