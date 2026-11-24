from django.contrib import admin
from .models import Profile, Contact, Student, Attendance, Notice
# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')


@admin.register(Contact)
class ContactAdmin(admin. ModelAdmin):
    list_display = ['id', 'name', 'email', 'message', 'created_at']


@admin.register(Student)
class StudentAdmin(admin. ModelAdmin):
    list_display = ['id', 'name', 'roll_no', 'std']


@admin.register(Attendance)
class AttendanceAdmin(admin. ModelAdmin):
    list_display = ['id', 'student', 'date', 'present'] 



@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
