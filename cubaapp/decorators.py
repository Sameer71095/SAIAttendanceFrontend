from functools import wraps
from django.shortcuts import redirect

def login_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.session.get('user_id'):
            return function(request, *args, **kwargs)
        else:
            return redirect('indexlogin')
    return wrap