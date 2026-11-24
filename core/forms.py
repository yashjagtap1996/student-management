from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField,AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from .models import Student
from .models import Feedback

class SignUpForm (UserCreationForm):
    username=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        help_text=password_validation. password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control','unique': 'true'}),
    )
    class Meta:
        model = User
        fields = ("username", "email")
        field_classes = {'username': UsernameField}
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
            

class MySignInForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'})
    )
    password = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'}),
    )

from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your message...',
                'rows': 4
            }),
        }
        labels = {
            'name': 'Name',
            'email': 'Email',
            'message': 'Message',
        }
        error_messages = {
            'name': {
                'required': 'Please enter your name.',
            },
            'email': {
                'required': 'Please enter your email.',
                'invalid': 'Please enter a valid email address.',
            },
            'message': {
                'required': 'Please enter a message.',
            },
        }
        help_texts = {
            'name': 'Enter your name.',
            'email': 'Enter your email address.',
            'message': 'Enter your message.',
        }
        
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['roll_no', 'name', 'std']
        widgets = {
            'roll_no': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'std': forms.Select(attrs={'class': 'form-control'}),
        }

class FeedbackForm(forms.ModelForm):

    class Meta:
        model = Feedback

        fields = ['student_name', 'message']

        widgets = {

            'student_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your name'
            }),

            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Write your feedback'
            }),
        }