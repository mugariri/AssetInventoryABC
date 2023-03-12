from django.conf import settings


class SessionIdleTimeout(object):
    """Middle ware to ensure user gets logged out after defined period if inactvity."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import datetime
        from django.contrib.auth import authenticate, logout
        if request.user.is_authenticated:
            current_datetime = datetime.datetime.now()
            if 'last_active_time' in request.session:
                idle_period = (current_datetime - datetime.datetime.fromisoformat(
                    request.session['last_active_time'])).total_seconds()
                if idle_period > settings.SECURITY_SESSION_EXPIRE_AFTER:
                    logout(request)
            if not (request.path_info in settings.SECURITY_SESSION_PASSIVE_URLS):
                request.session['last_active_time'] = str(current_datetime)

        response = self.get_response(request)

        return response
