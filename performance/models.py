

from django.db import models

class StudentPerformance(models.Model):
    student_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    grade = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.student_name} - {self.subject}: {self.grade}"

    @classmethod
    def is_duplicate(cls, student_name, subject, grade):
        return cls.objects.filter(student_name=student_name, subject=subject, grade=grade).exists()
