import datetime
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .decorators import login_required
import requests
from . import models
import json
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from requests.exceptions import ConnectionError
from django.http import HttpResponse


#base_url='http://192.67.63.238:5000/api'
#base_url='http://127.0.0.1:5049/api' #local
base_url='http://127.0.0.1:5000/api'  #live

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
    token = request.session.get('token')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'bearer ' + token
    }
   
    employerId = request.session.get('employerId')
    
    try:
        response = requests.post(base_url + '/Employee/GetAllEmployees?employerId=' + str(employerId), headers=headers)
    except ConnectionError:
        messages.error(request, 'Unable to connect to the server. Please try again later.')
        context = {"breadcrumb": {"parent": "Employees", "child": "Employees"}}
        return render(request, 'employee-list/employees.html', context)

    response_data = json.loads(response.text)

    if response_data['isSuccess']:
        context = {
            "breadcrumb": {"parent": "Employees", "child": "Employees"},
            "employees": response_data['data']
        }
        return render(request, 'employee-list/employees.html', context)
    else:
        return JsonResponse({"error": "Failed to fetch employees"}, status=400)


@login_required
def addEmployee(request):
    salary_types = []
    
    token = request.session.get('token')
    
    # Add the JSON content-type header
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'bearer ' + token
    }
    
    try:
        response = requests.post(base_url + '/salarytype/getsalarytype', headers=headers)
    except ConnectionError:
        messages.error(request, 'Unable to connect to the server. Please try again later.')
        return render(request, 'add-employee/addemployee.html', {'breadcrumb': {'parent': 'Employees', 'child': 'Employees'}})
    
    if response.ok:
        # Deserialize the response from JSON to a Python object
        response_data = json.loads(response.content)
        
        # Verify the response data
        if response_data['isSuccess']:
            data = response_data['data']
            salary_types = [{'id': s['salaryTypeId'], 'name': s['salaryTypeName']} for s in data]
    
    departments = []
    try:
        responses = requests.post(base_url + '/department/GetDepartments', headers=headers)
    except ConnectionError:
        messages.error(request, 'Unable to connect to the server. Please try again later.')
        return render(request, 'add-employee/addemployee.html', {'breadcrumb': {'parent': 'Employees', 'child': 'Employees'}})
    
    if responses.ok:
        # Deserialize the response from JSON to a Python object
        response_datas = json.loads(responses.content)
        
        # Verify the response data
        if response_datas['isSuccess']:
            datas = response_datas['data']
            departments = [{'id': s['departmentId'], 'name': s['departmentName']} for s in datas]
    
    locations = []
    
    employerId = request.session.get('employerId')
    request_data = {
        'EmployerID': employerId
    }
    request_data_json = json.dumps(request_data)
    
    try:
        responsess = requests.post(base_url + '/location/getlocations', headers=headers)
    except ConnectionError:
        messages.error(request, 'Unable to connect to the server. Please try again later.')
        return render(request, 'add-employee/addemployee.html', {'breadcrumb': {'parent': 'Employees', 'child': 'Employees'}})
    
    if responsess.ok:
        # Deserialize the response from JSON to a Python object
        response_datass = json.loads(responsess.content)
        
        # Verify the response data
        if response_datass['isSuccess']:
            datass = response_datass['data']
            locations = [{'id': s['locationId'], 'name': s['name']} for s in datass]
    
    context = {
        'breadcrumb': {'parent': 'Employees', 'child': 'Employees'},
        'departments': departments,
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

        try:
            # Send the login request to the API and get the response
            response = requests.post(base_url + '/employer/login', data=login_data_json, headers=headers)
        except ConnectionError:
            messages.error(request, 'Unable to connect to the server. Please try again later.')
            return render(request, 'login/login.html', {"breadcrumb": {"parent": "Dashboard", "child": "Login"}})

        # Deserialize the response from JSON to a Python object
        response_data = json.loads(response.content)

        # Verify the response data
        if response_data['isSuccess']:
            # Deserialize the response JSON into an entity
            entity = json.loads(response.text)
            
            # Save the entity in the secure cache with a timeout
            cache.set('user_data', entity, timeout=300000)  # 5 minutes timeout

            # Parse the data string as a JSON object
            data = response_data['data']
            request.session['user_id'] = data['employerId']
            request.session['employerId'] = data['employerId']
            request.session['token'] = data['token']
            request.session['name'] = data['name']
            request.session['phoneNumber'] = data['phoneNumber']
            request.session['address'] = data['address']
            request.session['is_authenticated'] = True
            request.session.set_expiry(30000)  # set session timeout to 5 minutes
            return redirect('index')
        else:
            messages.error(request, 'Incorrect email or password. Please try again.')
            return render(request, 'login/login.html', {"breadcrumb": {"parent": "Dashboard", "child": "Login"}})
    else:
        context = {"breadcrumb": {"parent": "Dashboard", "child": "Login"}}
        return render(request, 'login/login.html', context)
    
    
    
def logout_view(request):
         request.session.clear()
         context = {"breadcrumb": {"parent": "Dashboard", "child": "Login"}}
         return redirect('indexlogin')
      
      

def validate_data(data):
    try:
        validate_email(data['email'])
    except ValidationError:
        return False, "Invalid email format."
    
    if not data['contact'].isdigit():
        return False, "Contact number should only contain digits."
    
    if data['salary'] < 0:
        return False, "Salary should be a positive number."
    
    if data['max_monthly_overtime'] < 0:
        return False, "Max monthly overtime should be a positive number."
    
    return True, ""

def submit_form(request):
      if request.method == 'POST':
        # Collect data from the submitted form
         data = {
            'name': str(request.POST.get('Name')),
            'email': str(request.POST.get('Email')),
            'contact': str(request.POST.get('Contact')),
            'unique_id': str(request.POST.get('UniqueId')),
            'weekend_days': request.POST.getlist('days'),
            'salary': float(request.POST.get('salary')),
            'salary_type': int(request.POST.get('salaryType')),
            'department': int(request.POST.get('department')),
            'designation': str(request.POST.get('designation')),
            'starting_date': str(request.POST.get('startingDate')),
            'end_date': str(request.POST.get('endDate')),
            'is_overtime': bool(request.POST.get('isOvertime')),
            'is_location_bound': bool(request.POST.get('isLocationBound')),
            'location': int(request.POST.get('location')),
            # 'workday_start': datetime.datetime.strptime(request.POST.get('workdayStart'), '%H:%M').time().strftime('%H:%M:%S'),
            # 'workday_end': datetime.datetime.strptime(request.POST.get('workdayEnd'), '%H:%M').time().strftime('%H:%M:%S'),
            'max_monthly_overtime': int(request.POST.get('maxMonthlyOvertime')),
            'description': str(request.POST.get('Description'))
         }
         try:
            data['workday_start'] = datetime.datetime.strptime(request.POST.get('workdayStart'), '%H:%M').time().strftime('%H:%M:%S')
            data['workday_end'] = datetime.datetime.strptime(request.POST.get('workdayEnd'), '%H:%M').time().strftime('%H:%M:%S')
         except ValueError:
            messages.error(request, "Invalid time format. Please enter a valid time in the format 'HH:MM'.")
            return redirect(request.path)
          # Validate required fields
         required_fields = ['name', 'email', 'contact', 'unique_id', 'salary', 'salary_type', 'department', 'designation', 'starting_date', 'end_date', 'is_overtime', 'is_location_bound', 'location', 'workday_start', 'workday_end', 'max_monthly_overtime']
         missing_fields = [field for field in required_fields if not data[field]]

         if missing_fields:
            messages.error(request, "Missing required fields: {}".format(", ".join(missing_fields)))
            return redirect(request.path)

        # Validate data types and values
         is_valid, error_message = validate_data(data)
         if not is_valid:
            messages.error(request, error_message)
            return redirect(request.path)


        # Convert data to JSON
         json_data = json.dumps(data)

        # Call the POST API
         api_url = base_url + '/employee/addemployee'
         
   
         token = request.session.get('token')
   
        
        # Add the JSON content-type header
         headers = {
      'Content-Type': 'application/json',
      'Authorization': 'bearer ' + token
      }
         response = requests.post(api_url, data=json_data, headers=headers)

         if response.status_code == 200:  # Change this to the appropriate status code for a successful response
            return redirect('index')
      else:
        # Handle GET requests by returning an error message or rendering a form template
        return HttpResponse("This endpoint only accepts POST requests.", status=405)
        # Or render a form template:
        # return render(request, 'path/to/your/form_template.html')
         
         
         
         
