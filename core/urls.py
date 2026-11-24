from django.urls import path
from core import views

urlpatterns = [
    path('',views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('sign-up/', views.SignupView, name='signup'),
    path('sign-in/', views.SigninView, name='signin'),
    path('logout/', views.LogoutView, name='logout'),
    path('attendance/', views.mark_attendance, name='mark_attendance'),
    path('add-student/', views.add_student, name='add_student'),
    path('delete-student/<int:pk>', views.delete_student, name='delete_student'),
    path('edit-student/<int:pk>', views.edit_student, name='edit_student'),
    path('view-student/', views.view_student, name='view_student'),
    path('download-csv/', views.download_csv, name='download_csv'),
    path('dashboard/', views.attendance_dashboard, name='attendance_dashboard'),
    path('notices/', views.notice_list, name='notice_list'),
    path("student/attendance/",views.student_attendance_view,name="student_attendance"),
    path('feedback/', views.feedback_view, name='feedback'),
    path('chatbot-page/', views.chatbot_page, name='chatbot_page'),
    path('ai-chatbot/', views.ai_chatbot, name='ai_chatbot'),
]