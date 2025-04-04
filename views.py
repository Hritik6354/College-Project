from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_protect
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime,date,time
from django.contrib.auth.views import PasswordResetView
from django.utils import timezone
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import os



# Create your views here.
# @csrf_protect
# def Login(request):
#     if request.session.get('username'):
#         user = User.objects.get(username=request.session.get('username'))
#         emp_id = Employee.objects.filter(user=user).first()
#         context = {
#             'username' : request.session.get('username'),
#             'emp' : emp_id ,
#             'is_hr' : emp_id.is_hr
#         }
#         return render(request,'index.html',context)
#     else:
#         if request.method == 'POST':
#             username = request.POST.get('username')
#             password = request.POST.get('password')

#             user = authenticate(username=username,password=password)

#             if user is not None:
#                 emp_id = Employee.objects.filter(user=user).first()
#                 login(request,user)
#                 request.session['username'] = username
#                 context = {
#                     'is_hr' : emp_id.is_hr,
#                     'emp' : emp_id
#                 }
#                 return render(request,'index.html',context)
            
#             else:


    
#                 if User.objects.filter(username=username).exists():
#                     messages.warning(request,'your password is incorrect')
#                 else:
#                     messages.warning(request,"your Username is incorrect")
#             return render(request,"login.html")
        
@csrf_protect
def Login(request):
    if request.session.get('username'):
        # If the user is already logged in, redirect to the index page
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            emp_id = Employee.objects.filter(user=user).first()
            login(request, user)
            request.session['username'] = username
            
            # Redirect to index to fetch and show data
            return redirect('index')
        else:
            if User.objects.filter(username=username).exists():
                messages.warning(request, 'Your password is incorrect')
            else:
                messages.warning(request, "Your username is incorrect")

    return render(request, "login.html")

def ask_Security_Questions(request):
    if request.method == 'POST':
        answer1 = request.POST.get('answer1')
        answer2 = request.POST.get('answer2')
        answer3 = request.POST.get('answer3')

        username = request.user.username  # Assuming the user is logged in

        try:
            # Find the employee record
            employee = Employee.objects.get(user__username=username)
            # Save answers in the Employee model (you need to create fields for answers)
            employee.security_answer_1 = answer1  # You must add these fields in your Employee model
            employee.security_answer_2 = answer2
            employee.security_answer_3 = answer3
            employee.save()

            messages.success(request, 'Your answers have been saved successfully.')
            return redirect('Login')  # Redirect to the home page after successful save
        except Employee.DoesNotExist:
            messages.error(request, 'Employee record does not exist.')

    return render(request, 'ask_security_questions.html')


def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        answer1 = request.POST.get('answer1')
        answer2 = request.POST.get('answer2')
        answer3 = request.POST.get('answer3')
        try:
            user = Employee.objects.get(user__username=username)
            if (user.security_answer_1 == answer1 and 
                user.security_answer_2 == answer2 and 
                user.security_answer_3 == answer3):
                # Generate and send OTP or token here
                user.generate_reset_token()
                messages.success(request, 'Answers are correct. You can reset your password now.')
                messages.success(request,f'token:{user.reset_token}')             
                return redirect('reset_password')  # Redirect to reset password view
            else:
                messages.error(request, 'Incorrect answers. Please try again.')
            
        except Employee.DoesNotExist:
            messages.warning(request,f'Username : {username} does not exist')
            return render(request,"forgot_password.html") 
    return render(request,"forgot_password.html")


def reset_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        token = request.POST.get('token')
        new_password = request.POST.get('new_password')
        
        try:
            user = Employee.objects.get(user__username=username, reset_token=token)
            if user.token_expiration >= timezone.now():
                user.user.set_password(new_password)
                user.user.save()
                # user.password = new_password  # Ideally, hash the password
                user.reset_token = None  # Clear the reset token after use
                user.token_expiration = None
                user.save()
                messages.success(request, 'Password has been reset successfully.')
                return redirect('Login')
            else:
                messages.error(request, 'Token has expired')
        except Employee.DoesNotExist:
            messages.error(request, 'Invalid token or user')

    return render(request, 'reset_password.html')


def Logout(request):
    if 'username' in request.session:
        del request.session['username']
        logout(request)
      
    return redirect('Login')



def add_Employee(request):
    if request.method == 'POST':
        profile = request.FILES.get('profile')
        emp_id = request.POST.get('user')
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        email = request.POST.get('email')
        mob = request.POST.get('mob')
        address = request.POST.get('address')
        dob = request.POST.get('dob')
        date_of_joining = request.POST.get('date_of_join')
        state = request.POST.get('state')
        city = request.POST.get('city')
        department = request.POST.get('department')
        designation = request.POST.get('designation')
        password = request.POST.get('password')
        c_password = request.POST.get('c_password')

        if(state):
            state_id = State.objects.get(state_name=state)
            
        if(city):
            city_id = City.objects.get(city_name=city)

        if(department):
            department_id = Department.objects.get(dep_name=department)

        if(designation):
            designation_id = Designation.objects.get(des_name=designation)
        
        user_id  = User.objects.create(username=emp_id,first_name=first_name,last_name=last_name,email=email)
        user_id.set_password(password)
        user_id.save()

        emp_id = Employee.objects.create(user=user_id,profile=profile,email=email,mobile_number=mob,
                                         dob=dob,date_of_joining=date_of_joining,emp_address=address,
                                         dep_id=department_id,des_id=designation_id,state_id=state_id,
                                         city_id=city_id,is_employee=True)
        
        messages.success(request, f'Employee {first_name} {last_name} has been added successfully!')
                 

    user = User.objects.filter(username = request.session.get('username'))
    emp_id = Employee.objects.filter(user=user.first()).first()
    cities = City.objects.all()
    states = State.objects.all()
    departments = Department.objects.all()
    designations = Designation.objects.all()

      
                

    context = {
        'cities': cities,
        'states' : states,
        'departments' : departments,
        'designations' : designations,
        'is_hr' : emp_id.is_hr if emp_id else False
    }

    return render(request,"Employee/add_Employee.html",context)

#
def my_Profile(request):
    user = request.user

    # Get the employee profile associated with the user
    emp_id = get_object_or_404(Employee, user=user)
    context = {
        'emp': emp_id,
        'is_hr': emp_id.is_hr,
    }
    return render(request,"Employee/my_profile.html",context)

def view_Employee(request):
    user = request.user
    if request.method == 'POST':
        dep_name = request.POST.get('dep_filter')
        if dep_name == 'all':
            employess = Employee.objects.all()
        else:
            department = Department.objects.get(dep_name=dep_name)
            employess = Employee.objects.filter(dep_id=department)
        context = {
            'employees': employess,
            'departments' : Department.objects.all()
        }
        return render(request,'Employee/view_employee.html', context)
    

    # Get the employee profile associated with the user
    emp_id = get_object_or_404(Employee, user=user)
    user = User.objects.filter(username=request.session.get('username'))
    emp_id = Employee.objects.filter(user=user[0]).first()

    all_deps = Department.objects.all()

    # Check if the user is HR
    if emp_id.is_hr:
        # Get all employees if the user is HR
        context = {
            'departments': all_deps,
            'employees': Employee.objects.all(),
            'is_hr': emp_id.is_hr,  # Pass HR status to the template
        }
        return render(request, "Employee/view_employee.html", context)
    else:
        # If user is not HR, show an error message and redirect
        messages.error(request, "You do not have permission to view this page.")
        return redirect('index')  # Change this to the page you want non-HR users to be redirected to

def update_Employee(request,id):
    user = User.objects.filter(username= request.session.get('username')).first()
    emp_id = Employee.objects.filter(user=user).first()
    employee = Employee.objects.get(id = id)

    if request.method == 'POST':
        employee = get_object_or_404(Employee,id = id)

        vals = request.POST
        employee.user.first_name = vals.get('fname')
        employee.user.last_name = vals.get('lname')
        employee.user.save()
        employee.user.email = vals.get('email')
        employee.mobile_number = vals.get('mob')
        employee.emp_address = vals.get('address')
        employee.state_id = State.objects.filter(state_name=vals.get('state')).first()
        employee.city_id = City.objects.filter(city_name=vals.get('city')).first()
        employee.dep_id = Department.objects.filter(dep_name=vals.get('department')).first()
        employee.des_id = Designation.objects.filter(des_name=vals.get('designation')).first()
        employee.profile = request.FILES.get('profile')
        # if profile:
        #     employee.profile = profile

        employee.save()

        return redirect('view_Employee')
    else:
        cities = City.objects.all()
        states = State.objects.all()
        deps = Department.objects.all()
        designation = Designation.objects.all()

        context = {
            'employee': employee,
            'cities': cities,
            'states': states,
            'deps': deps,
            'designation': designation,
            'is_hr': emp_id.is_hr
        }
        
        # return render(request, 'update_employee.html', context)

        return render(request,'Employee/update_employee.html',context)

def delete_Employee(request,id):
    employee = get_object_or_404(Employee,id=id)

    user = User.objects.filter(username=request.session.get('username')).first()
    emp_id = Employee.objects.filter(user=user).first()

    if request.method == 'POST':
        employee.delete()
        return redirect('view_Employee')
    context = {
        'employee' : employee,
        'is_hr' :emp_id.is_hr
    }
    return render(request,'Employee/delete_employee.html',context)





def index(request):
    if not request.user.is_authenticated:
        return redirect('Login')

    # Employee and department count
    employee_count = Employee.objects.filter(is_employee=True).count()
    total_department = Department.objects.all().count()
    total_pending_leaves = Leaves.objects.filter(status='pending').count()
    present_employees = Attendance.objects.filter(att_date=datetime.now().date(), in_time__isnull=False).count()
    absent_employees = employee_count - present_employees
    total_pending_requests = RequestAttendance.objects.filter(status='pending').count()

    # Fetch user and related employee object
    user = User.objects.filter(username=request.session.get('username')).first()
    emp_id = Employee.objects.filter(user=user).first()

    # Handle case where emp_id might be None
    if emp_id is None:
        return redirect('Login')  # Or handle differently if needed

    # Attendance chart period logic
    period = request.GET.get('period', 'monthly')
    today = datetime.now().date()

    # Determine the start date based on the selected period
    if period == 'daily':
        start_date = today
    elif period == 'weekly':
        start_date = today - timedelta(days=7)
    elif period == 'monthly':
        start_date = today.replace(day=1)
    elif period == 'yearly':
        start_date = today.replace(month=1, day=1)
    else:
        start_date = today

    # Total employees
    total_employees = Employee.objects.count()

    # Fetch attendance records for the selected period
    attendance_records = Attendance.objects.filter(att_date__gte=start_date, att_date__lte=today)

    # Calculate daily attendance percentages
    daily_attendance = {}
    for date in attendance_records.values('att_date').distinct():
        att_date = date['att_date']
        present_count = attendance_records.filter(att_date=att_date).exclude(in_time__isnull=True).count()
        absent_count = total_employees - present_count
        present_percentage = (present_count / total_employees) * 100
        absent_percentage = (absent_count / total_employees) * 100

        daily_attendance[att_date] = {
            'present_percentage': present_percentage,
            'absent_percentage': absent_percentage
        }

    # Prepare data for the attendance bar chart
    dates = list(daily_attendance.keys())
    present_percentages = [daily_attendance[date]['present_percentage'] for date in dates]
    absent_percentages = [daily_attendance[date]['absent_percentage'] for date in dates]

    # Attendance bar chart creation
    attendance_fig = go.Figure()
    attendance_fig.add_trace(go.Bar(
        x=dates, y=present_percentages, name='Present (%)', marker_color='green',
        text=[f'{p:.1f}%' for p in present_percentages], textposition='auto'
    ))
    attendance_fig.add_trace(go.Bar(
        x=dates, y=absent_percentages, name='Absent (%)', marker_color='red',
        text=[f'{a:.1f}%' for a in absent_percentages], textposition='auto'
    ))

    attendance_fig.update_layout(
        title=f"Attendance Percentage ({period.capitalize()})",
        xaxis_title="Date",
        yaxis_title="Percentage of Employees",
        barmode='group',
        plot_bgcolor='#2d2d2d',
        font_color='white',
        width=700  # Adjust width to fit alongside pie chart
    )

    attendance_chart_html = attendance_fig.to_html(full_html=False, include_plotlyjs=False)

    # Leaves chart logic
    leaves = Leaves.objects.filter(fro__gte=start_date, fro__lte=today) 
    if leaves.exists():
        total_approved = leaves.filter(status='approved').count()
        total_pending = leaves.filter(status='pending').count()
        total_rejected = leaves.filter(status='rejected').count()
    else:
        total_approved = 0
        total_pending = 0
        total_rejected = 0
        
    if total_approved == 0 and total_pending == 0 and total_rejected == 0:
        # If all values are zero, create a dummy pie chart to show "No data available"
        leave_labels = ['No data']
        leave_values = [1]  # Use a dummy value for plotting
        leave_colors = ['gray']
    else:
        # Normal pie chart with actual data
        leave_labels = ['Approved', 'Pending', 'Rejected']
        leave_values = [total_approved, total_pending, total_rejected]
        leave_colors = ['green', 'yellow', 'red']

    # Leave pie chart creation
    leave_fig = go.Figure(data=[go.Pie(labels=leave_labels, values=leave_values, hole=.4, marker=dict(colors=leave_colors))])
    leave_fig.update_layout(
        title_text=f"Leave Status Distribution ({period.capitalize()})",
        showlegend=True,
        paper_bgcolor='#2d2d2d',
        font_color='white',
        width=500  # Adjust width to fit alongside bar chart
    )

    leave_chart_html = leave_fig.to_html(full_html=False, include_plotlyjs=False)

    # Employee-specific data
    pending_leaves = Leaves.objects.filter(emp_id=emp_id, status='pending').count()
    approved_leaves = Leaves.objects.filter(emp_id=emp_id, status='approved').count()
    remaining_leave_days = Leavetype.objects.filter(leaves__emp_id=emp_id).values('name', 'remaining_days')

    # Present/Absent status for today
    attendance_today = Attendance.objects.filter(emp_id=emp_id, att_date=today).exists()
    present_status = 'P' if attendance_today else 'A'

    # Leave requests and attendance records for current month
    current_month_leaves = Leaves.objects.filter(emp_id=emp_id, fro__month=today.month).count()
    attendance_current_month = Attendance.objects.filter(emp_id=emp_id, att_date__month=today.month).count()
    pending_attendance_requests = RequestAttendance.objects.filter(emp_id=emp_id,status='pending').count()

    context = {
        'employee_count': employee_count,
        'total_department': total_department,
        'total_pending_leaves': total_pending_leaves,
        'present_employees': present_employees,
        'absent_employees': absent_employees,
        'total_pending_requests': total_pending_requests,
        'attendance_chart_html': attendance_chart_html,
        'leave_chart_html': leave_chart_html,
        'period': period,
        'is_hr': emp_id.is_hr,
        'emp_id':emp_id,

        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'remaining_leave_days': remaining_leave_days,
        'present_status': present_status,
        'current_month_leaves': current_month_leaves,
        'attendance_current_month': attendance_current_month,
        'pending_attendance_requests':pending_attendance_requests
        # 'is_employee': emp_id.is_employee
    }

    return render(request, "index.html", context)



#
def add_Departmet(request):
    user = User.objects.filter(username=request.session.get('username')).first()
    emp_id = Employee.objects.filter(user=user).first()
    if request.method == 'POST':
        dep_name = request.POST.get('dep_name')
        dep = Department.objects.filter(dep_name=dep_name)
        if dep:
            messages.warning(request,'Department Already Exists !')
        else:
            Department.objects.create(dep_name=dep_name)
            messages.success(request,'Department Added Successfully')
    return render(request,"Department/add_department.html",{'is_hr': emp_id.is_hr,})

def view_Department(request):
    user = User.objects.filter(username=request.session.get('username')).first()
    emp_id = Employee.objects.filter(user=user).first()
    context = {
        'dep' : Department.objects.all(),
        'is_hr': emp_id.is_hr,
    }
    return render(request,"Department/view_department.html",context)

#
@login_required
@csrf_protect
def fill_Attendance(request):
        #Get user object
        user = request.user
        # Initialize context with username
        context = {'username' : user.username}

         # Get the employee object
        emp = Employee.objects.filter(user=user).first()
        context['is_hr'] = emp.is_hr

        if(emp):
            att_obj = Attendance.objects.filter(att_date=date.today(),emp_id=emp).first()

            if att_obj:
                context['in_time'] = att_obj.in_time
                context['out_time'] = att_obj.out_time

            if request.method == 'POST':
                if 'check_in' in request.POST:
                    #check if user has already checked in for the day
                    if att_obj:
                        context['message'] = 'you have already checked in today'
                    else:
                        att_date = date.today()
                        # in_time = time.strptime("%H:%M:%S",time.localtime())
                        in_time = datetime.now().strftime("%H:%M:%S") 
                        att_obj = Attendance.objects.create(emp_id=emp,att_date=att_date,in_time=in_time)
                        context['in_time'] = att_obj.in_time
                        context['message'] = 'check in successfull'

                    return render(request,'Attendance/fill_attendance.html',context)
            
                if 'check_out' in request.POST:
                    if not att_obj:
                        context['message'] = 'you have not checked in yet' 
                    # elif not att_obj.out_time:
                    #     context['message'] = 'you have not checked out today'
                    else:
                        att_obj.out_time = datetime.now().strftime("%H:%M:%S") 
                        att_obj.save()
                        context['in_time'] = att_obj.in_time
                        context['out_time'] = att_obj.out_time
                        context['message'] = 'checked-out successfull'
                    return render(request,"Attendance/fill_attendance.html",context)
      

        return render(request,"Attendance/fill_attendance.html",context)

@login_required
@csrf_protect
def attendace_Request(request):
        user = request.user
        emp = Employee.objects.filter(user=user).first()
        if request.method == 'POST':
            RequestAttendance.objects.create(
                emp_id =emp , att_date = request.POST.get('att_date'), in_time =request.POST.get('intime'),
                out_time =request.POST.get('outtime'),request_type=request.POST.get('request_type'),
                status = 'pending',note = request.POST.get('not')
            )
            messages.success(request, 'your request sent successfully')

        return render(request,"Attendance/attendace_request.html",{'is_hr': emp.is_hr})

@login_required
def approve_Attendance(request):
    user = request.user
    emp = Employee.objects.filter(user=user).first()

    all_requests = RequestAttendance.objects.filter(status='pending')
    return render(request, 'Attendance/approve_attendance.html', context={'attendance_records': 
                                                                          all_requests, 'is_hr':emp.is_hr})



def accept_Reject_Attendance(request,attendance_id,action):
    user =request.user
    emp = Employee.objects.filter(user=user).first()
    attendance = get_object_or_404(RequestAttendance,id=attendance_id)
    if attendance:
        if action == "approve" and attendance.request_type == 'new':
            att_obj = Attendance.objects.filter(att_date=attendance.att_date,emp_id=attendance.emp_id).first()
            if not att_obj:
                Attendance.objects.create(
                    emp_id = attendance.emp_id,
                    att_date = attendance.att_date,
                    in_time = attendance.in_time,
                    out_time = attendance.out_time
                )
                attendance.status = 'approved'
            else:
                return HttpResponse(f"Already have attendence for date {attendance.att_date} either you can create a change request")    

        elif action == "approve" and attendance.request_type=='change':
            att_obj = Attendance.objects.filter(att_date=attendance.att_date,emp_id=attendance.emp_id).first()
            if att_obj:
                att_obj.in_time = attendance.in_time
                att_obj.out_time = attendance.out_time
                att_obj.save()
                attendance.status ="approved"
            else:
                return HttpResponse("No records found for select date")
        
        elif action == "reject":
            attendance.status = 'rejected'

    attendance.save()
    all_requests = RequestAttendance.objects.filter(status='pending')
    context = {
        'attendance_records' : all_requests,
        'is_hr':emp.is_hr,
    }
    return render(request,"Attendance/approve_attendance.html",context)



# def show_Graph(request):
#     user = User.objects.filter(username=request.session.get('username')).first()
#     emp_id = get_object_or_404(Employee, user=user) 
#    # Default to the current month
#     today = timezone.now().date()
#     first_day = today.replace(day=1)
#     attendance_data = Attendance.objects.filter(att_date__range=(first_day, today))

#     # If the user submits custom dates
#     if request.method == 'POST':
#         from_date = request.POST.get('from_date')
#         to_date = request.POST.get('to_date')
#         if from_date and to_date:
#             attendance_data = Attendance.objects.filter(att_date__range=(from_date, to_date))

#     # Convert queryset to DataFrame
#     data = {
#         'Date': [att.att_date for att in attendance_data],
#         'In Time': [att.in_time.hour + att.in_time.minute / 60 if att.in_time else 0 for att in attendance_data],
#         'Out Time': [att.out_time.hour + att.out_time.minute / 60 if att.out_time else 0 for att in attendance_data],
#     }
#     df = pd.DataFrame(data)

#     # Create Plotly bar chart
#     fig = px.bar(df, x='Date', y=['In Time', 'Out Time'],
#                  title='Attendance Analysis',
#                  labels={'value': 'Time (Hours)', 'variable': 'Type'},
#                  barmode='group')

#     # Convert to HTML
#     graph_html = fig.to_html(full_html=False)

#     context = {
#         'graph_html': graph_html,
#         'is_hr': emp_id.is_hr,
#     }
#     return render(request,"Attendance/show_graph.html",context)

from django.utils import timezone
from datetime import timedelta, datetime
import pandas as pd
import plotly.express as px
from django.shortcuts import render, get_object_or_404

def show_Graph(request):
    user = User.objects.filter(username=request.session.get('username')).first()
    emp_id = get_object_or_404(Employee, user=user) 

    # Default to the current month
    today = timezone.now().date()
    first_day = today.replace(day=1)
    one_year_ago = today - timedelta(days=365)  # Calculate one year ago

    # Initialize message variable
    show_warning_message = False

    # If the user submits custom dates
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        if from_date and to_date:
            # Convert from_date and to_date to date objects
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            # Check if the range is more than one year for HR users
            if emp_id.is_hr and (to_date - from_date).days > 365:
                show_warning_message = True
                from_date = max(from_date, one_year_ago)
                to_date = today  # Restrict end date to today if range exceeds one year

            attendance_data = Attendance.objects.filter(att_date__range=(from_date, to_date))
        else:
            # If no dates provided, fall back to default for current month
            attendance_data = Attendance.objects.filter(att_date__range=(first_day, today))
    else:
        # Default to current month if no POST request
        attendance_data = Attendance.objects.filter(att_date__range=(first_day, today))

    # Convert queryset to DataFrame
    data = {
        'Date': [att.att_date for att in attendance_data],
        'In Time': [att.in_time.hour + att.in_time.minute / 60 if att.in_time else 0 for att in attendance_data],
        'Out Time': [att.out_time.hour + att.out_time.minute / 60 if att.out_time else 0 for att in attendance_data],
    }
    df = pd.DataFrame(data)

    # Create Plotly bar chart
    fig = px.bar(df, x='Date', y=['In Time', 'Out Time'],
                 title='Attendance Analysis',
                 labels={'value': 'Time (Hours)', 'variable': 'Type'},
                 barmode='group')

    # Convert to HTML
    graph_html = fig.to_html(full_html=False)

    context = {
        'graph_html': graph_html,
        'is_hr': emp_id.is_hr,
        'show_warning_message': show_warning_message,  # Pass message flag to the template
    }
    return render(request, "Attendance/show_graph.html", context)



@login_required
def view_Attendance(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    employee = request.GET.get('employee')
    all_emp = Employee.objects.all()

    user = request.user
    emp = Employee.objects.filter(user=user).first()

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if employee and emp.is_hr:
            selected_emp = get_object_or_404(Employee, user__username = employee)
            if selected_emp:
                attendances = Attendance.objects.filter(emp_id=selected_emp, att_date__range=(start_date, end_date))
            else:
                attendances = Attendance.objects.filter(att_date__range=(start_date, end_date))
        else:
            attendances = Attendance.objects.filter(emp_id=emp, att_date__range=(start_date, end_date))

        context = {
            'attendances': attendances,
            'start_date': start_date,
            'end_date': end_date,
            'is_hr': emp.is_hr,
            'all_emp': all_emp,
        } 
        
        return render(request,"Attendance/view_attendance.html",context)
    else:
        if employee and emp.is_hr:
            selected_emp = get_object_or_404(Employee, user__username = employee)
            if selected_emp:
                attendances = Attendance.objects.filter(emp_id=selected_emp)
          
        else:
            attendances = Attendance.objects.filter(emp_id=emp)

        context = {
            'attendances': attendances,
            'start_date': start_date,
            'end_date': end_date,
            'is_hr': emp.is_hr,
            'all_emp': all_emp,
        } 
        
        return render(request,"Attendance/view_attendance.html",context)

    return render(request, "Attendance/view_attendance.html", {
        'start_date': None,
        'end_date': None,
        'all_emp': all_emp, 
        'is_hr': emp.is_hr
    })


@login_required
def leave_Application(request):
    leavetype = Leavetype.objects.all()
    user = request.user
    emp_id = Employee.objects.filter(user=user).first()

    if request.method == 'POST':
        fro = request.POST.get('start_date')
        to = request.POST.get('end_date')
        leave_type = request.POST.get('leave_type')
        description = request.POST.get('description')

        # Convert the input strings to date objects
        fro_date = datetime.strptime(fro, '%Y-%m-%d').date()
        to_date = datetime.strptime(to, '%Y-%m-%d').date()

        overlapping_leave = Leaves.objects.filter(
            emp_id=emp_id, fro__lte=to_date, to__gte=fro_date, status__in=['pending', 'approved']
        ).first()

        if overlapping_leave:
            messages.warning(request, 'You have already applied for leave on overlapping dates')
        else:
            if leave_type:
                leavetype_id = Leavetype.objects.filter(name=leave_type).first()
                num_of_days = (to_date - fro_date).days + 1

                # Check if the employee has enough remaining days for the selected leave type
                if leavetype_id.remaining_days >= num_of_days:
                    leave = Leaves.objects.create(
                        emp_id=emp_id,
                        fro=fro_date,  # Use fro_date which is a date object
                        to=to_date,  # Use to_date which is a date object
                        num_of_days=num_of_days,
                        leavetype_id=leavetype_id,
                        description=description
                    )
                    leave.save()
                    messages.success(request, f"You have successfully applied for {num_of_days} days leave")
                else:
                    messages.warning(request, f"You only have {leavetype_id.remaining_days} days remaining for {leave_type} leave")
            else:
                messages.error(request, "Leave type is required")
        
        return render(request, "Leave/leave_application.html", {'leavetype': leavetype, 'is_hr': emp_id.is_hr})

    context = {
        'leavetype': leavetype,
        'is_hr': emp_id.is_hr
    }

    return render(request, "Leave/leave_application.html", context)


@login_required
@csrf_protect
def leave_Approve(request):
    employee = request.GET.get('employee')
    emp_id = Employee.objects.filter(user__username=employee).first()

    status = request.GET.get('status')
    leave_records = Leaves.objects.select_related('leavetype_id','emp_id').all()

    leave_records = leave_records.exclude(status__in=['approved', 'rejected'])
    if employee and status:
        leave_records = leave_records.filter(emp_id=emp_id,status=status)

    elif employee:
        leave_records = leave_records.filter(emp_id=emp_id)
    
    elif status:
        leave_records = leave_records.filter(status=status)
    

    user = request.user
    emp = Employee.objects.filter(user=user).first()
    context = {
        'leave_records' : leave_records,
        'all_emp' : Employee.objects.all(),
        'is_hr' : emp.is_hr
    }
    return render(request,"Leave/leave_approve.html",context)

def approve_Reject_leave(request,id,action):
    user = request.user
    emp_id = Employee.objects.filter(user=user).first()

    # leave_records = Leaves.objects.select_related('leavetype_id','emp_id').all()
    # context = {
    #     'leave_records' : leave_records,
    #     'all_emp' : Employee.objects.all(),
    #     'is_hr' : emp_id.is_hr
    # }
    leave = Leaves.objects.get(id=id)

    if action == 'accept':
        leave.status = 'approved'
        leave.save()
        messages.success(request, "Leave has been approved.")
        return render(request,'Leave/leave_approve.html')
    
    if action == 'reject':
        leave.status = 'rejected'
        leave.save()
        messages.warning(request, "Leave has been rejected.")
    return render(request,'Leave/leave_approve.html')


def track_Leave(request):
    user = User.objects.filter(username=request.session.get('username')).first()
    emp_id = Employee.objects.filter(user=user).first()
    leave_records = Leaves.objects.filter(emp_id=emp_id).exclude(status='cancle')

    context = {
        'leave_records' : leave_records,
        'all_emp' : Employee.objects.all(),
        'is_hr' : emp_id.is_hr
    }
    return render(request,"Leave/track_leave.html",context)


def cancel_Leave(request,id):
    leave = get_object_or_404(Leaves,id=id)
    user = User.objects.filter(username=request.session.get('username')).first()
    emp_id = Employee.objects.filter(user=user).first()
   

   

    if leave.status == 'pending':
        leave.status = 'cancle'
        leave.save()
        messages.success(request,"The leave has been successed")
    else:
        messages.warning(request,"The leave cannot be canelled as it is not in pending status")

    leave_records = Leaves.objects.filter(emp_id=emp_id,status='cancle')

    context = {
        'leave_records' : leave_records,
        'all_emp' : Employee.objects.all(),
        'today' : date.today(),
        'is_hr' : emp_id.is_hr,
    }
    return render(request,"Leave/track_leave.html",context)


@login_required
def change_Password(request):
   
    if request.method == 'POST':
       
        current_password = request.POST.get('currentpassword')
        new_password = request.POST.get('newpassword')
        confirm_password = request.POST.get('confirmpassword')
        
        # Implement your password change logic here
        user = request.user
        if user.check_password(current_password) and new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            messages.success(request,"your Password Updated succcessfully")
            return render(request, 'change_password.html')

        elif(new_password != confirm_password):
            messages.success(request," password and confirm password are not same ")
            return render(request, 'change_password.html')
        else:
            messages.success(request,"Your current password is wrong, try Again...")
            return render(request, 'change_password.html')
         
    user = User.objects.filter(username=request.session.get('username')).first()
    emp = Employee.objects.filter(user=user).first()

    return render(request, 'change_password.html',{'is_hr':emp.is_hr})

def about_us(request):
    user = User.objects.filter(username=request.session.get('username')).first()
    emp = Employee.objects.filter(user=user).first()
    return render(request,'about_us.html',{'is_hr':emp.is_hr})

def contect_us(request):
    user = User.objects.filter(username=request.session.get('username')).first()
    emp = Employee.objects.filter(user=user).first()
    return render(request,'contect_us.html',{'is_hr':emp.is_hr})

# @login_required
# def download_attendance_csv(request, start_date, end_date):
#     start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
#     end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

#     user = request.user
#     emp = Employee.objects.filter(user=user).first()

#     attendances = Attendance.objects.filter(emp_id=emp, att_date__range=(start_date, end_date))

#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="attendance_report_{emp}.csv"'

#     writer = csv.writer(response)
#     writer.writerow(['Date', 'In Time', 'Out Time'])  # Add more headers as needed

#     for attendance in attendances:
#         writer.writerow([attendance.att_date, attendance.in_time, attendance.out_time])

#     return response


import csv
@login_required
def download_attendance_csv(request, start_date, end_date):
    try:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status=400)

    user = request.user
    emp = Employee.objects.filter(user=user).first()

    attendances = Attendance.objects.filter(emp_id=emp, att_date__range=(start_date, end_date))

    if not attendances.exists():
        return HttpResponse("No attendance records found for the given date range.", status=404)

    # Prepare the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{emp}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'In Time', 'Out Time', 'Status'])  # Add other columns if needed

    for attendance in attendances:
        writer.writerow([
            attendance.att_date.strftime('%Y-%m-%d'), 
            attendance.in_time.strftime('%H:%M:%S') if attendance.in_time else 'N/A', 
            attendance.out_time.strftime('%H:%M:%S') if attendance.out_time else 'N/A',
            'Present'  # Add status logic if necessary
        ])

    return response
