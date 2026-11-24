from django.shortcuts import render, redirect
from .forms import SignUpForm, MySignInForm, ContactForm, StudentForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile,Notice  
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from .decorators import superuser_required
from .models import Student, Attendance
from django.http import HttpResponse
import csv
from .filters import StudentFilter, AttendanceFilter
from django.db.models import Count, Q
import json
from textblob import TextBlob
from .models import Feedback
from .forms import FeedbackForm
from django.http import JsonResponse
from difflib import get_close_matches
from django.db.models import Count
from datetime import date







def home(request):
    return render(request, 'core/home.html')



def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})


def SignupView(request):

    if request.method == 'POST':

        form = SignUpForm(request.POST)

        if form.is_valid():

            # CREATE USER
            user = form.save(commit=False)

            # DIRECTLY ACTIVATE USER
            user.is_active = True
            user.save()

            # CREATE PROFILE
            Profile.objects.create(user=user)

            messages.success(request, "Account created successfully")

            return redirect('signin')

        else:
            messages.error(request, "Please correct the errors below")

    else:
        form = SignUpForm()

    context = {
        'form': form
    }

    return render(request, 'core/sign-up.html', context)


def SigninView(request):

    if request.method == 'POST':

        form = MySignInForm(request=request, data=request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                # ACTIVATE OLD USERS IF INACTIVE
                if not user.is_active:
                    user.is_active = True
                    user.save()

                login(request, user)

                messages.success(request, "Login successful")

                return redirect('home')

        else:
            messages.error(request, "Invalid username or password")

    else:
        form = MySignInForm()

    context = {
        'form': form
    }

    return render(request, 'core/sign-in.html', context)

def LogoutView(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('signin')


    
def mark_attendance(request):
    students = Student.objects.all()

    student_filter = StudentFilter(request.GET, queryset=students)

    if request.method == 'POST':
        date = request.POST.get('date')

        for student in students:
            status = request.POST.get(str(student.id))  # checkbox value

            Attendance.objects.update_or_create(
                student=student,
                date=date,
                defaults={
                    'present': True if status == 'on' else False
                }
            )

        return redirect('mark_attendance')

    return render(request, 'core/attendance.html', { 'students': student_filter.qs,
        'filter': student_filter})


def view_student(request):
    students = Student.objects.all()

    student_filter = StudentFilter(request.GET, queryset=students)

    return render(request, 'core/read_student.html', {
        'students': student_filter.qs,
        'filter': student_filter
    })

def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_student')
    else:
        form = StudentForm()
    return render(request, 'core/add_student.html', {'form': form})

def edit_student(request, pk):
    student = Student.objects.get(pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('view_student')
    else:
        form = StudentForm(instance=student)
    return render(request, 'core/edit_student.html', {'form': form})

def delete_student(request, pk):
    student = Student.objects.get(pk=pk)
    student.delete()
    return redirect('view_student')

def download_csv(request):
    attendance_qs = Attendance.objects.select_related('student')
    attendance_filter = AttendanceFilter(request.GET, queryset=attendance_qs)

    # If download button clicked
    if 'download' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance.csv"'

        writer = csv.writer(response)
        writer.writerow(['Roll No', 'Name', 'Date', 'Present'])

        for att in attendance_filter.qs:
            writer.writerow([
                att.student.roll_no,
                att.student.name,
                att.date,
                'Yes' if att.present else 'No'
            ])

        return response

    return render(request, 'core/download.html', {
        'filter': attendance_filter
    })

def attendance_dashboard(request):
    data = []
    total_records_all = 0

    for std, _ in Student.std_choices:
        total = Attendance.objects.filter(student__std=std).count()
        present = Attendance.objects.filter(student__std=std, present=True).count()

        percentage = round((present / total) * 100, 2) if total > 0 else 0

        total_records_all += total

        data.append({
            'std': std,
            'total': total,
            'present': present,
            'percentage': percentage
        })

    # ✅ ignore std with 0 records for best/worst
    valid_data = [d for d in data if d['total'] > 0]

    highest = max(valid_data, key=lambda x: x['percentage'], default={'percentage': 0, 'std': '-'})
    lowest = min(valid_data, key=lambda x: x['percentage'], default={'percentage': 0, 'std': '-'})

    return render(request, 'core/dashboard.html', {
        'data': data,
        'highest': highest,
        'lowest': lowest,
        'total_records_all': total_records_all
    })


def notice_list(request):
    notices = Notice.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'core/notice_list.html', {'notices': notices})


from django.shortcuts import render
from .models import Student, Attendance

from django.shortcuts import render
from .models import Student, Attendance

def student_attendance_view(request):
    attendances = None
    message = None

    total = present = absent = percentage = 0

    if request.method == "POST":
        roll_no = request.POST.get("roll_no")
        name = request.POST.get("name")
        standard = request.POST.get("standard")

        try:
            student = Student.objects.get(
                roll_no=roll_no,
                name__iexact=name,
                std__iexact=standard
            )

            attendances = Attendance.objects.filter(
                student=student
            ).order_by("-date")

            total = attendances.count()
            present = attendances.filter(present=True).count()
            absent = total - present
            percentage = round((present / total) * 100, 2) if total else 0

            if total == 0:
                message = "No attendance records found."

        except Student.DoesNotExist:
            message = "Student not found. Please check details."

    return render(request, "core/student_attendance.html", {
        "attendances": attendances,
        "total": total,
        "present": present,
        "absent": absent,
        "percentage": percentage,
        "message": message
    })

def feedback_view(request):

    if request.method == 'POST':

        form = FeedbackForm(request.POST)

        if form.is_valid():

            feedback = form.save(commit=False)

            # NLP ANALYSIS
            analysis = TextBlob(feedback.message)

            polarity = analysis.sentiment.polarity

            # SENTIMENT DETECTION
            if polarity > 0:
                feedback.sentiment = 'Positive'

            elif polarity < 0:
                feedback.sentiment = 'Negative'

            else:
                feedback.sentiment = 'Neutral'

            feedback.save()

            messages.success(request, "Feedback submitted successfully")

            return redirect('feedback')

    else:
        form = FeedbackForm()

    feedbacks = Feedback.objects.all().order_by('-created_at')

    return render(request, 'core/feedback.html', {
        'form': form,
        'feedbacks': feedbacks
    })


def ai_chatbot(request):

    query = request.GET.get('query', '').lower()

    response = "Sorry, I could not understand your question."

    # =========================
    # STATIC NLP KNOWLEDGE
    # =========================

    knowledge_base = {

        "how to login":
        "Use your username and password on signin page.",

        "how to add student":
        "Admin can add students from manage menu.",

        "how to mark attendance":
        "Admin can mark attendance from attendance section.",

        "how to download csv":
        "Open download csv page from manage menu.",

        "how to view notices":
        "Click on notice section in navbar.",

        "what is this project":
        "This is an AI powered student management system.",

        "how to check attendance":
        "Students can use check attendance button in navbar."
    }

    # =========================
    # DYNAMIC DATABASE QUERIES
    # =========================

    # TOTAL STUDENTS
    if (
        "total students" in query or
        "how many students" in query
    ):

        total = Student.objects.count()

        response = f"Total students are {total}"


    # TOTAL FEEDBACKS
    elif (
        "total feedback" in query or
        "how many feedback" in query
    ):

        total = Feedback.objects.count()

        response = f"Total feedbacks are {total}"


    # PRESENT TODAY
    elif (
        "present today" in query or
        "students present" in query
    ):

        total = Attendance.objects.filter(
            date=date.today(),
            present=True
        ).count()

        response = (
            f"{total} students are present today"
        )


    # ABSENT TODAY
    elif (
        "absent today" in query or
        "students absent" in query
    ):

        total_students = Student.objects.count()

        present = Attendance.objects.filter(
            date=date.today(),
            present=True
        ).count()

        absent = total_students - present

        response = (
            f"{absent} students are absent today"
        )


    # ACTIVE NOTICES
    elif (
        "show notices" in query or
        "active notices" in query
    ):

        notices = Notice.objects.filter(
            is_active=True
        )

        if notices.exists():

            titles = []

            for notice in notices[:5]:
                titles.append(notice.title)

            response = (
                "Current notices are: " +
                ", ".join(titles)
            )

        else:

            response = "No active notices found."


    # HIGHEST ATTENDANCE CLASS
    elif (
        "highest attendance" in query or
        "best attendance" in query
    ):

        best_class = None
        best_percentage = 0

        for std, _ in Student.std_choices:

            total = Attendance.objects.filter(
                student__std=std
            ).count()

            present = Attendance.objects.filter(
                student__std=std,
                present=True
            ).count()

            if total > 0:

                percentage = (
                    (present / total) * 100
                )

                if percentage > best_percentage:

                    best_percentage = percentage
                    best_class = std

        if best_class:

            response = (
                f"Class {best_class} has the highest "
                f"attendance with "
                f"{round(best_percentage, 2)} percent"
            )

        else:

            response = (
                "No attendance data found."
            )


    # LOWEST ATTENDANCE CLASS
    elif (
        "lowest attendance" in query or
        "worst attendance" in query
    ):

        worst_class = None
        worst_percentage = 101

        for std, _ in Student.std_choices:

            total = Attendance.objects.filter(
                student__std=std
            ).count()

            present = Attendance.objects.filter(
                student__std=std,
                present=True
            ).count()

            if total > 0:

                percentage = (
                    (present / total) * 100
                )

                if percentage < worst_percentage:

                    worst_percentage = percentage
                    worst_class = std

        if worst_class:

            response = (
                f"Class {worst_class} has the lowest "
                f"attendance with "
                f"{round(worst_percentage, 2)} percent"
            )

        else:

            response = (
                "No attendance data found."
            )


    # TOTAL ACTIVE NOTICES
    elif (
        "how many notices" in query or
        "total notices" in query
    ):

        total = Notice.objects.filter(
            is_active=True
        ).count()

        response = (
            f"There are {total} active notices"
        )


    # NLP FAQ MATCHING
    else:

        matches = get_close_matches(
            query,
            knowledge_base.keys(),
            n=1,
            cutoff=0.3
        )

        if matches:

            response = knowledge_base[matches[0]]
    

    return JsonResponse({
        'response': response
    })

def chatbot_page(request):

    return render(
        request,
        'core/chatbot.html'
    )

    
def ai_chatbot(request):    

    query = request.GET.get('query', '').lower()

    response = "Sorry, I could not understand your question."

    # =========================
    # STATIC NLP KNOWLEDGE
    # =========================

    knowledge_base = {

        "how to login":
        "Use your username and password on signin page.",

        "how to add student":
        "Admin can add students from manage menu.",

        "how to mark attendance":
        "Admin can mark attendance from attendance section.",

        "how to download csv":
        "Open download csv page from manage menu.",

        "how to view notices":
        "Click on notice section in navbar.",

        "what is this project":
        "This is an AI powered student management system.",

        "how to check attendance":
        "Students can use check attendance button in navbar.",

        "how to edit student":
        "Go to student section and click edit button.",

        "how to logout":
        "Click logout button in navbar.",

        "how to contact admin":
        "Use contact form available in navbar.",

        "how to view dashboard":
        "Dashboard is available in manage menu."
    }

    # =========================
    # DYNAMIC DATABASE QUERIES
    # =========================

    # TOTAL STUDENTS
    if (
        "total students" in query or
        "how many students" in query
    ):

        total = Student.objects.count()

        response = f"Total students are {total}"


    # TOTAL FEEDBACKS
    elif (
        "total feedback" in query or
        "how many feedback" in query
    ):

        total = Feedback.objects.count()

        response = f"Total feedbacks are {total}"


    # PRESENT TODAY
    elif (
        "present today" in query or
        "students present" in query
    ):

        total = Attendance.objects.filter(
            date=date.today(),
            present=True
        ).count()

        response = (
            f"{total} students are present today"
        )


    # ABSENT TODAY
    elif (
        "absent today" in query or
        "students absent" in query
    ):

        total_students = Student.objects.count()

        present = Attendance.objects.filter(
            date=date.today(),
            present=True
        ).count()

        absent = total_students - present

        response = (
            f"{absent} students are absent today"
        )


    # ACTIVE NOTICES
    elif (
        "show notices" in query or
        "active notices" in query
    ):

        notices = Notice.objects.filter(
            is_active=True
        )

        if notices.exists():

            titles = []

            for notice in notices[:5]:
                titles.append(notice.title)

            response = (
                "Current notices are: " +
                ", ".join(titles)
            )

        else:

            response = "No active notices found."


    # HIGHEST ATTENDANCE
    elif (
        "highest attendance" in query or
        "best attendance" in query
    ):

        best_class = None
        best_percentage = 0

        for std, _ in Student.std_choices:

            total = Attendance.objects.filter(
                student__std=std
            ).count()

            present = Attendance.objects.filter(
                student__std=std,
                present=True
            ).count()

            if total > 0:

                percentage = (
                    (present / total) * 100
                )

                if percentage > best_percentage:

                    best_percentage = percentage
                    best_class = std

        if best_class:

            response = (
                f"Class {best_class} has the highest "
                f"attendance with "
                f"{round(best_percentage, 2)} percent"
            )

        else:

            response = (
                "No attendance data found."
            )


    # LOWEST ATTENDANCE
    elif (
        "lowest attendance" in query or
        "worst attendance" in query
    ):

        worst_class = None
        worst_percentage = 101

        for std, _ in Student.std_choices:

            total = Attendance.objects.filter(
                student__std=std
            ).count()

            present = Attendance.objects.filter(
                student__std=std,
                present=True
            ).count()

            if total > 0:

                percentage = (
                    (present / total) * 100
                )

                if percentage < worst_percentage:

                    worst_percentage = percentage
                    worst_class = std

        if worst_class:

            response = (
                f"Class {worst_class} has the lowest "
                f"attendance with "
                f"{round(worst_percentage, 2)} percent"
            )

        else:

            response = (
                "No attendance data found."
            )


    # TOTAL NOTICES
    elif (
        "how many notices" in query or
        "total notices" in query
    ):

        total = Notice.objects.filter(
            is_active=True
        ).count()

        response = (
            f"There are {total} active notices"
        )


    # TOTAL PRESENT RECORDS
    elif (
        "total present" in query or
        "present records" in query
    ):

        total = Attendance.objects.filter(
            present=True
        ).count()

        response = (
            f"Total present records are {total}"
        )


    # TOTAL ABSENT RECORDS
    elif (
        "total absent" in query or
        "absent records" in query
    ):

        total = Attendance.objects.filter(
            present=False
        ).count()

        response = (
            f"Total absent records are {total}"
        )


    # TOTAL CLASSES
    elif (
        "total classes" in query or
        "how many classes" in query
    ):

        total = len(Student.std_choices)

        response = (
            f"There are {total} classes"
        )


    # STUDENTS IN CLASS
    elif (
        "students in class" in query or
        "how many students in class" in query
    ):

        found = False

        for std, _ in Student.std_choices:

            if std.lower() in query:

                total = Student.objects.filter(
                    std=std
                ).count()

                response = (
                    f"There are {total} students "
                    f"in class {std}"
                )

                found = True
                break

        if not found:

            response = (
                "Please mention valid class."
            )


    # LATEST NOTICE
    elif (
        "latest notice" in query or
        "recent notice" in query
    ):

        notice = Notice.objects.filter(
            is_active=True
        ).order_by('-created_at').first()

        if notice:

            response = (
                f"Latest notice is "
                f"{notice.title}"
            )

        else:

            response = (
                "No notices available."
            )


    # READ NOTICE
    elif (
        "read notice" in query or
        "notice message" in query
    ):

        notice = Notice.objects.filter(
            is_active=True
        ).order_by('-created_at').first()

        if notice:

            response = (
                f"{notice.title}. "
                f"{notice.message}"
            )

        else:

            response = (
                "No notices available."
            )


    # TOTAL ATTENDANCE
    elif (
        "total attendance" in query or
        "attendance records" in query
    ):

        total = Attendance.objects.count()

        response = (
            f"Total attendance records are {total}"
        )


    # POSITIVE FEEDBACK
    elif (
        "positive feedback" in query
    ):

        total = Feedback.objects.filter(
            sentiment='Positive'
        ).count()

        response = (
            f"Total positive feedbacks are {total}"
        )


    # NEGATIVE FEEDBACK
    elif (
        "negative feedback" in query
    ):

        total = Feedback.objects.filter(
            sentiment='Negative'
        ).count()

        response = (
            f"Total negative feedbacks are {total}"
        )


    # NEUTRAL FEEDBACK
    elif (
        "neutral feedback" in query
    ):

        total = Feedback.objects.filter(
            sentiment='Neutral'
        ).count()

        response = (
            f"Total neutral feedbacks are {total}"
        )


    # ABOUT PROJECT
    elif (
        "who created this project" in query or
        "about project" in query
    ):

        response = (
            "This is an AI powered Student "
            "Management System built using "
            "Django, Bootstrap and NLP."
        )


    # NLP FAQ MATCHING
    else:

        matches = get_close_matches(
            query,
            knowledge_base.keys(),
            n=1,
            cutoff=0.3
        )

        if matches:

            response = knowledge_base[matches[0]]

    return JsonResponse({
        'response': response
    })