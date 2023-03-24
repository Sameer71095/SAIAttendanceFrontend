

from django.shortcuts import render, redirect

class CustomLoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is authenticated
        # if not request.session.get('user_id'):
        #     # User is not authenticated, redirect to login page
        #     return redirect('indexlogin')
        
        # User is authenticated, continue with the request/response cycle
        response = self.get_response(request)
        return response