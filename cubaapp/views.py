from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .decorators import login_required
import requests
from . import models
import json
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt

#base_url='http://192.67.63.238:5000/api'
#base_url='http://127.0.0.1:5049/api'
base_url='http://127.0.0.1:5000/api'

#@login_required
def indexPage(request):
   context={"breadcrumb":{"parent":"Dashboard","child":"Stater-kit"}}
   return render(request,'general/index.html',context)

@login_required
def index(request):
   context={"breadcrumb":{"parent":"Dashboard","child":"Dashboard"}}
   return render(request,'default/index2.html',context)


@login_required
def viewEmployee(request):
   context={"breadcrumb":{"parent":"Employees","child":"Employees"}}
   return render(request,'employee-list/employees.html',context)


@login_required
def addEmployee(request):
   salary_types = []
   
   token = request.session.get('token')
   
        
        # Add the JSON content-type header
   headers = {'Content-Type': 'application/json'}
   headers = {'Authorization': 'bearer '+token}
        
   response = requests.post(base_url + '/salarytype/getsalarytype', headers=headers)
   if response.ok:
          
        # Deserialize the response from JSON to a Python object
        response_data = json.loads(response.content)
        
        # Verify the response data
        if response_data['isSuccess']:
            
            data = response_data['data']
     # data = response.json().get('data')
            salary_types = [{'id': s['salaryTypeId'], 'name': s['salaryTypeName']} for s in data]
      
   departments = []
   responses = requests.post(base_url + '/department/GetDepartments', headers=headers)
   if responses.ok:
      
        # Deserialize the response from JSON to a Python object
        response_datas = json.loads(responses.content)
        
        # Verify the response data
        if response_datas['isSuccess']:
            
            datas = response_datas['data']
      #datas = responses.json().get('data')
            departments = [{'id': s['departmentId'], 'name': s['departmentName']} for s in datas]
      
   locations = []
   
        # Serialize the login data to JSON
   request_data = {
            'EmployerID': 1
        }
   request_data_json = json.dumps(request_data)
   responsess = requests.post(base_url + '/location/getlocations', headers=headers)
   if responsess.ok:
      
        # Deserialize the response from JSON to a Python object
        response_datass = json.loads(responsess.content)
        
        # Verify the response data
        if response_datass['isSuccess']:
            
            datass = response_datass['data']
    #  datass = responsess.json().get('data')
            locations = [{'id': s['locationId'], 'name': s['name']} for s in datass]
      
   context = {
   'breadcrumb': {'parent': 'Employees', 'child': 'Employees'},
   'departments': departments ,
   'salary_types': salary_types,
   'locations': locations
   }
   return render(request, 'add-employee/addemployee.html', context)



def login_view(request):
       
   if request.session.get('user_id'):
      # user is already logged in, redirect to index
      return redirect('index')
   if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # Serialize the login data to JSON
        login_data = {
            'email': email,
            'password': password
        }
        login_data_json = json.dumps(login_data)
        
        # Add the JSON content-type header
        headers = {'Content-Type': 'application/json'}
        
        # Send the login request to the API and get the response
        response = requests.post(base_url + '/employer/login', data=login_data_json, headers=headers)
        
        # Deserialize the response from JSON to a Python object
        response_data = json.loads(response.content)
        
        # Verify the response data
        if response_data['isSuccess']:
            # Save the response data to a secure local cache
            # ...            
            # Deserialize the response JSON into an entity
            entity = json.loads(response.text)
            # Save the entity in the secure cache
            cache.set('user_data', entity, timeout=300000)
            
            # Log the user in to the Django app
          #  user = authenticate(request, email=email, password=password)
           # if user is not None:
             #   login(request, user)
            # Parse the data string as a JSON object
            data = response_data['data']
            request.session['user_id'] = data['employerId']
            request.session['token'] = data['token']
            request.session['name'] = data['name']
            request.session['phoneNumber'] = data['phoneNumber']
            request.session['address'] = data['address']
            request.session['is_authenticated'] = True
            request.session.set_expiry(30000) # set session timeout to 5 minutes
            return redirect('index')
          #  else:
           #    context = {"breadcrumb": {"parent": "Dashboard", "child": "Login"}, "error": "Invalid form data"}
           #    return render(request, 'login/login.html', context)
   else:
               context = {"breadcrumb": {"parent": "Dashboard", "child": "Login"}}
               return render(request, 'login/login.html', context)
          
     
 
def logout_view(request):
         request.session.clear()
         context = {"breadcrumb": {"parent": "Dashboard", "child": "Login"}}
         return redirect('indexlogin')
      
      
      

def submit_form(request):
      if request.method == 'POST':
        # Collect data from the submitted form
         data = {
            'name': request.POST.get('Name'),
            'email': request.POST.get('Email'),
            'contact': request.POST.get('Contact'),
            'unique_id': request.POST.get('UniqueId'),
            'weekend_days': request.POST.getlist('days'),
            'salary': request.POST.get('salary'),
            'salary_type': request.POST.get('salaryType'),
            'department': request.POST.get('department'),
            'designation': request.POST.get('designation'),
            'starting_date': request.POST.get('startingDate'),
            'end_date': request.POST.get('endDate'),
            'is_overtime': request.POST.get('isOvertime'),
            'is_location_bound': request.POST.get('isLocationBound'),
            'location': request.POST.get('location'),
            'workday_start': request.POST.get('workdayStart'),
            'workday_end': request.POST.get('workdayEnd'),
            'max_monthly_overtime': request.POST.get('maxMonthlyOvertime'),
            'description': request.POST.get('Description')
        }
          # Validate required fields
         required_fields = ['name', 'email', 'contact', 'unique_id', 'salary', 'salary_type', 'department', 'designation', 'starting_date', 'end_date', 'is_overtime', 'is_location_bound', 'location', 'workday_start', 'workday_end', 'max_monthly_overtime']
         missing_fields = [field for field in required_fields if not data[field]]

         if missing_fields:
            return JsonResponse({"error": "Missing required fields.", "missing_fields": missing_fields}, status=400)


        # Convert data to JSON
         json_data = json.dumps(data)

        # Call the POST API
         api_url = base_url + '/employee/addemployee'
         
   
         token = request.session.get('token')
   
        
        # Add the JSON content-type header
         headers = {'Content-Type': 'application/json'}
         headers = {'Authorization': 'bearer '+token}
         response = requests.post(api_url, data=json_data, headers=headers)

         if response.status_code == 200:  # Change this to the appropriate status code for a successful response
            return redirect('index')
         
         
         
         
         
