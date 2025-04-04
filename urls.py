from django.urls import path,include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf import settings
from .views import *

urlpatterns = [
   path('',Login,name="Login"),
   path('ask_Security_Questions/', ask_Security_Questions, name='ask_Security_Questions'),
   path('forgot_password/', forgot_password, name='forgot_password'),
   path('reset_password/', reset_password, name='reset_password'),
   path('Logout/',Logout,name="Logout"),
   path('index/',index,name="index"),

   #
   path('my_Profile/',my_Profile,name="my_Profile"),
   path('add_Employee/',add_Employee,name="add_Employee"),
   path('view_Employee/',view_Employee,name="view_Employee"),
   path('update_Employee<int:id>/',update_Employee,name="update_Employee"),
   path('delete_Employee<int:id>/',delete_Employee,name="delete_Employee"),

   #
   path('add_Departmet/',add_Departmet,name="add_Departmet"),
   path('view_Department/',view_Department,name="view_Department"),

   #
   path('fill_Attendance/',fill_Attendance,name="fill_Attendance"),
   path('attendace_Request/',attendace_Request,name="attendace_Request"),
   path('approve_Attendance/',approve_Attendance,name="approve_Attendance"),
   path('accept_Reject_Attendance/<int:attendance_id>/<str:action>',accept_Reject_Attendance,name="accept_Reject_Attendance"),
   path('show_Graph/',show_Graph,name="show_Graph"),
   path('view_Attendance/',view_Attendance,name="view_Attendance"),
   #

   path('leave_Application/',leave_Application,name="leave_Application"),
   path('leave_Approve/',leave_Approve,name="leave_Approve"),
   path('approve_Reject_leave/<int:id>/<str:action>',approve_Reject_leave,name="approve_Reject_leave"),
   path('track_Leave/',track_Leave,name="track_Leave"),
   path('cancel_Leave/<int:id>',cancel_Leave,name="cancel_Leave"),

   #
   path('change_Password',change_Password,name="change_Password"),

   #
    path('about_us',about_us,name="about_us"),
    path('contect_us',contect_us,name="contect_us"),
    path('download_attendance_csv',download_attendance_csv,name="download_attendance_csv"),
   
   #
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    
   

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)