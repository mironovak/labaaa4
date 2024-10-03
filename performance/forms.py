from django import forms

class StudentPerformanceForm(forms.Form):
    student_name = forms.CharField(max_length=100)
    subject = forms.CharField(max_length=100)
    grade = forms.CharField(max_length=10)
