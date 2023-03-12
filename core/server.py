from waitress import serve

from core.wsgi import application

if __name__ == '__main__':
    serve(application, port='8001')

def run(start: True):
    if start:
        serve(application, host="10.106.60.5", port='8000')