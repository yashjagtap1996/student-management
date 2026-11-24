import django_filters
from .models import Student, Attendance

class StudentFilter(django_filters.FilterSet):
    class Meta:
        model = Student
        fields = ['std']

class AttendanceFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(
        field_name='date',
        lookup_expr='exact',
        widget=django_filters.widgets.forms.DateInput(attrs={'type': 'date'})
    )

    std = django_filters.ChoiceFilter(
        field_name='student__std',
        choices=Student.std_choices,
        label='Standard'
    )

    class Meta:
        model = Attendance
        fields = ['date', 'std']

