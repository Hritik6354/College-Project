from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import uuid
from datetime import datetime
from django.utils import timezone
from datetime import timedelta



# Create your models here.
class Department(models.Model):
    id = models.BigAutoField(unique=True,primary_key=True)
    dep_name = models.CharField(max_length=50)

    def __str__(self):
        return self.dep_name

class Designation(models.Model):
    id = models.BigAutoField(unique=True,primary_key=True)
    des_name = models.CharField(max_length=50)   
    
    def __str__(self):
        return self.des_name
    
class State(models.Model):
    id = models.BigAutoField(unique=True,primary_key=True)
    state_name = models.CharField(max_length=50)

    def __str__(self):
        return self.state_name
    
class City(models.Model):
    id = models.BigAutoField(unique=True,primary_key=True)
    city_name = models.CharField(max_length=50)
    # state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return self.city_name


phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
class Employee(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    id = models.BigAutoField(unique=True,primary_key=True)
    profile = models.ImageField(upload_to="images/",blank=True,null=True)
    email = models.EmailField()
    mobile_number = models.CharField(validators=[phone_regex],max_length=17,blank=True)
    gender = models.CharField(max_length=5,default='Male')
    dob = models.DateField()
    date_of_joining = models.DateField()
    emp_address = models.TextField(max_length=10000)
    dep_id = models.ForeignKey(Department,null=True,blank=True,on_delete=models.CASCADE)
    des_id = models.ForeignKey(Designation,null=True,blank=True,on_delete=models.CASCADE)
    reset_token = models.UUIDField(default=None,null=True,blank=True)
    token_expiration = models.DateTimeField(null=True,blank=True)
    security_answer_1 = models.CharField(max_length=255, blank=True, null=True)
    security_answer_2 = models.CharField(max_length=255, blank=True, null=True)
    security_answer_3 = models.CharField(max_length=255, blank=True, null=True)
    state_id = models.ForeignKey(State,null=True,blank=True,on_delete=models.CASCADE)
    city_id = models.ForeignKey(City,null=True,blank=True,on_delete=models.CASCADE)
    
    is_hr = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
    def generate_reset_token(self):
        self.reset_token = uuid.uuid4()
        self.token_expiration = timezone.now() + timedelta(minutes=1)
        self.save()

class Leavetype(models.Model):
    id = models.BigAutoField(unique=True,primary_key=True)
    name = models.CharField(max_length=30)
    annual_limit = models.IntegerField(default=0)  # Annual limit for this leave type
    days_taken = models.IntegerField(default=0)  # Days already taken
    remaining_days = models.IntegerField(default=0)  # Remaining days

    def save(self, *args, **kwargs):
        self.remaining_days = self.annual_limit - self.days_taken  # Calculate remaining days
        super(Leavetype, self).save(*args, **kwargs)

    def increment_days_taken(self, days):
        """Increment the days taken and update the remaining days."""
        self.days_taken += days
        self.remaining_days = self.annual_limit - self.days_taken
        self.save()

    def decrement_days_taken(self, days):
        """Decrement the days taken and update the remaining days."""
        self.days_taken -= days
        self.remaining_days = self.annual_limit - self.days_taken
        self.save()

    def __str__(self):
        return self.name
    

class Leaves(models.Model):
    # id = models.BigAutoField(unique=True,blank=True)
    emp_id = models.ForeignKey(Employee,on_delete=models.CASCADE,default=None)
    leavetype_id = models.ForeignKey(Leavetype,on_delete=models.CASCADE, default=None)
    fro = models.DateTimeField()
    to = models.DateField(null=True)
    num_of_days = models.FloatField(default=0)
    status = models.CharField(max_length=30,choices = [('pending','pending'),('approved','approved'),('cancle','cancle'),('rejected','rejected')],default='pending')
    description = models.TextField(null=True)

    def save(self, *args, **kwargs):
        # Calculate the number of leave days
        # leave_days = (self.to - self.fro).days + 1
        # leavetype = self.leavetype_id

        if self.to:  # Ensure 'to' date is provided
            leave_days = (self.to - self.fro.date()).days + 1  # Convert fro to date
            self.num_of_days = leave_days  # Set num_of_days
            
            leavetype = self.leavetype_id
        
        # Handling leave approval
        if self.status == 'approved' and not self.pk:
            # If the leave is being approved for the first time
            leavetype.increment_days_taken(leave_days)
        
        # Handling leave cancellation or rejection after approval
        elif self.status in ['cancelled', 'rejected'] and self.pk:
            # Revert days if the leave was previously approved
            original_leave = Leaves.objects.get(pk=self.pk)
            if original_leave.status == 'approved':
                leavetype.decrement_days_taken(original_leave.num_of_days)

        # Save the leave request
        super(Leaves, self).save(*args, **kwargs)


    def __str__(self):
        return self.emp_id.user.email
    
class Attendance(models.Model):
    id = models.BigAutoField(unique=True,primary_key=True)
    emp_id = models.ForeignKey(Employee,null=True,blank=True,on_delete=models.CASCADE)
    att_date = models.DateField()
    in_time = models.TimeField(null=True,blank=True)
    out_time = models.TimeField(null=True,blank=True)

    def __str__(self):
        return self.emp_id.user.email

class RequestAttendance(models.Model):
    id = models.BigAutoField(unique=True,primary_key=True)
    emp_id = models.ForeignKey(Employee,null=True,blank=True,on_delete=models.CASCADE)
    att_date = models.DateField()
    in_time = models.TimeField()
    out_time = models.TimeField(null=True,blank=True)
    request_type = models.CharField(max_length=10,choices=[('new','New Request'),('change','Change Request')])
    status = models.CharField(max_length=20,choices=[('pending','pending'),('approved','approved'),('cancle','cancle'),('rejected','rejected')],default='pending')
    note =  models.TextField(max_length=300,null=True,blank=True)

    def __str__(self):
        return self.emp_id.user.email
    

