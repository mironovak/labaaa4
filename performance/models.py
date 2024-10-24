

from django.db import models

# Определяет класс модели StudentPerformance, который наследует от models.Model. 
# Это означает, что класс будет представлять таблицу в базе данных.
class StudentPerformance(models.Model):
    # создание поля
    student_name = models.CharField(max_length=100) 
    subject = models.CharField(max_length=100)
    grade = models.CharField(max_length=10)

#  Определяет метод __str__, который возвращает строковое представление объекта модели. 
    def __str__(self):
        # Возвращает строку, содержащую имя студента, предмет и оценку в формате "Имя - Предмет: Оценка".
        return f"{self.student_name} - {self.subject}: {self.grade}"

# Декоратор, который указывает, что метод is_duplicate является методом класса. 
    @classmethod
    # Определяет метод класса is_duplicate, 
    # который проверяет наличие дубликата записи в базе данных на основе имени студента, предмета и оценки.
    def is_duplicate(cls, student_name, subject, grade):
        # Выполняет запрос к базе данных для поиска записей с теми же значениями полей и возвращает True, 
        # если такая запись существует; иначе — False.
        return cls.objects.filter(student_name=student_name, subject=subject, grade=grade).exists()
