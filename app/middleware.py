from datetime import datetime
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect

from app.views import user_logout


class SessionExpiredMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(request):
        last_activity = request.session['last_activity']
        now = datetime.now()
        print(request.session['last_activity'])
        if (now - last_activity).minutes > 10:
            user_logout(request)
            return HttpResponseRedirect("LOGIN_PAGE_URL")
        if (now - last_activity).minutes < 10:
            print("still young")
        if not request.is_ajax():
            # don't set this for ajax requests or else your
            # expired session checks will keep the session from
            # expiring :)
            request.session['last_activity'] = now

        def process_exception(self, request, exception):
            return HttpResponse("in exception")


class ExceptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        return HttpResponse("in exception")


class ExceptionHandlingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        print(exception)
        print("passed here Exception")
        return HttpResponse("in exception")


from django.http import Http404, HttpResponse


class Custom404Middleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            # implement your custom logic. You can send
            # http response with any template or message
            # here. unicode(exception) will give the custom
            # error message that was passed.
            msg = "" #unicode(exception)
            return HttpResponse(msg, status=404)


class CheckUpdatedEmployee(object):
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        return self.get_response(request)

    def check_employee_profile(self, request):
        # print(request)
        if not request.user.employee.updated:
            print("passed here also")
            return redirect('abcassetsmanager:user_update')
