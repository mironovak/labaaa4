
import xml.etree.ElementTree as ET
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .forms import StudentPerformanceForm, DataSourceForm
from .models import StudentPerformance
from django.views.decorators.csrf import csrf_exempt



def home(request):
    return render(request, 'performance/home.html')

def upload_xml(request):
    if request.method == 'POST':
        form = StudentPerformanceForm(request.POST)
        if form.is_valid():
            student_name = form.cleaned_data['student_name']
            subject = form.cleaned_data['subject']
            grade = form.cleaned_data['grade']
            save_to = form.cleaned_data['save_to']

            if save_to == 'file':
                # Сохранение данных в XML-файл
                root = ET.Element("root")
                student = ET.SubElement(root, "student")
                ET.SubElement(student, "name").text = student_name
                ET.SubElement(student, "subject").text = subject
                ET.SubElement(student, "grade").text = grade
                tree = ET.ElementTree(root)
                file_path = os.path.join(settings.MEDIA_ROOT, f"{student_name}_{subject}.xml")
                tree.write(file_path)
            elif save_to == 'db':
                # Сохранение данных в базу данных
                if StudentPerformance.is_duplicate(student_name, subject, grade):
                    return HttpResponse("Найдена дублирующая запись. Не сохранено в базу данных.")
                StudentPerformance.objects.create(student_name=student_name, subject=subject, grade=grade)

            return redirect('list_data')  # Перенаправление на list_data
    else:
        form = StudentPerformanceForm()
    return render(request, 'performance/upload.html', {'form': form})

def list_xml(request):
    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)
    files = os.listdir(settings.MEDIA_ROOT)
    if not files:
        return HttpResponse("No XML files found.")
    return render(request, 'performance/list.html', {'files': files})


def upload_file(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            file_path = os.path.join(settings.MEDIA_ROOT, file.name)

            # Сохранение файла
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Проверка существования файла
            if not os.path.exists(file_path):
                return HttpResponse(f"File not found: {file_path}")

            # Проверка валидности XML-файла
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                print(root)
            except ET.ParseError as e:
                os.remove(file_path)
                print(f"XML parsing error: {e}")
                return HttpResponse("Invalid XML file.")
            except Exception as e:
                os.remove(file_path)
                print(f"Unexpected error: {e}")
                return HttpResponse("An unexpected error occurred.")

            return redirect('list_xml')
        else:
            return HttpResponse('No file was uploaded')
    return render(request, 'performance/upload_file.html')


def search_db(request):
    query = request.GET.get('query')
    if query:
        results = StudentPerformance.objects.filter(student_name__icontains=query) | \
                  StudentPerformance.objects.filter(subject__icontains=query) | \
                  StudentPerformance.objects.filter(grade__icontains=query)
        data = [{'student_name': result.student_name, 'subject': result.subject, 'grade': result.grade} for result in results]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

def edit_db(request, pk):
    if request.method == 'POST':
        student = StudentPerformance.objects.get(pk=pk)
        form = StudentPerformanceForm(request.POST)
        if form.is_valid():
            student.student_name = form.cleaned_data['student_name']
            student.subject = form.cleaned_data['subject']
            student.grade = form.cleaned_data['grade']
            student.save()
            return redirect('list_db')
    else:
        student = StudentPerformance.objects.get(pk=pk)
        form = StudentPerformanceForm(initial={'student_name': student.student_name, 'subject': student.subject, 'grade': student.grade})
    return render(request, 'performance/edit.html', {'form': form})

def delete_db(request, pk):
    student = StudentPerformance.objects.get(pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('list_db')
    return render(request, 'performance/delete_db.html', {'student': student})

def list_db(request):
    students = StudentPerformance.objects.all()
    return render(request, 'performance/list_db.html', {'students': students})

def list_data(request):
    if request.method == 'POST':
        form = DataSourceForm(request.POST)
        if form.is_valid():
            source = form.cleaned_data['source']
            if source == 'file':
                return redirect('list_xml')
            elif source == 'db':
                return redirect('list_db')
    else:
        form = DataSourceForm()
    return render(request, 'performance/list_data.html', {'form': form})
 
def list_db(request):
    students = StudentPerformance.objects.all()
    return render(request, 'performance/list_db.html', {'students': students})

def search_page(request):
    return render(request, 'performance/search.html')


# @csrf_exempt
# def search_text(request):
#     query = request.GET.get('query', '')
#     if query:
#         results = ET.Element("results")
#         for filename in os.listdir(settings.MEDIA_ROOT):
#             if filename.endswith('.xml'):
#                 file_path = os.path.join(settings.MEDIA_ROOT, filename)
#                 tree = ET.parse(file_path)
#                 root = tree.getroot()
#                 for elem in root.iter():
#                     if query.lower() in elem.text.lower():
#                         result = ET.SubElement(results, "result")
#                         file_elem = ET.SubElement(result, "file")
#                         file_elem.text = filename
#                         text_elem = ET.SubElement(result, "text")
#                         text_elem.text = elem.text
#         return HttpResponse(ET.tostring(results, encoding='unicode'), content_type='application/xml')
#     return HttpResponse('<results></results>', content_type='application/xml')      


@csrf_exempt
def search_text(request):
    query = request.GET.get('query', '')
    results = ET.Element("results")

    if query:
        for filename in os.listdir(settings.MEDIA_ROOT):
            if filename.endswith('.xml'):
                file_path = os.path.join(settings.MEDIA_ROOT, filename)
                tree = ET.parse(file_path)
                root = tree.getroot()

                # Фильтрация по элементам student
                for student in root.findall('student'):
                    name = student.find('name').text
                    subject = student.find('subject').text
                    grade = student.find('grade').text
                    
                    # Проверка на соответствие имени или предмета
                    if query.lower() in name.lower() or query.lower() in subject.lower():
                        result_elem = ET.SubElement(results, "result")
                        file_elem = ET.SubElement(result_elem, "file")
                        file_elem.text = filename
                        text_elem = ET.SubElement(result_elem, "text")
                        text_elem.text = f"{name} - {subject}: {grade}"

    return HttpResponse(ET.tostring(results, encoding='unicode'), content_type='application/xml')