from waitress import serve

from core.wsgi import application

if __name__ == '__main__':
    serve(application, port='5630')