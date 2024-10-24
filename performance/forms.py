
from django import forms


# Определяет новую форму Django, которая будет использоваться для ввода данных о студентах.
class StudentPerformanceForm(forms.Form):
    # Создает текстовое поле для ввода имени студента с максимальной длиной 100 символов.
    student_name = forms.CharField(max_length=100)
    subject = forms.CharField(max_length=100)
    grade = forms.CharField(max_length=10)
    # Создает поле выбора (radio button) для выбора способа сохранения данных (в файл или в базу данных). choices 
    # определяет доступные варианты, 
    # а widget=forms.RadioSelect указывает, что это будет отображаться как радиокнопки.
    save_to = forms.ChoiceField(choices=[('file', 'File'), ('db', 'Database')], widget=forms.RadioSelect)

# Определяет другую форму для выбора источника данных.
class DataSourceForm(forms.Form):
    source = forms.ChoiceField(choices=[('file', 'File'), ('db', 'Database')], widget=forms.RadioSelect)  