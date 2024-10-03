# import os
# from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from django.conf import settings
# from .forms import StudentPerformanceForm
# import xml.etree.ElementTree as ET

# def home(request):
#     return render(request, 'performance/home.html')

# def upload_xml(request):
#     if request.method == 'POST':
#         form = StudentPerformanceForm(request.POST)
#         if form.is_valid():
#             student_name = form.cleaned_data['student_name']
#             subject = form.cleaned_data['subject']
#             grade = form.cleaned_data['grade']

#             # Сохранение данных в XML-файл
#             root = ET.Element("root")
#             student = ET.SubElement(root, "student")
#             ET.SubElement(student, "name").text = student_name
#             ET.SubElement(student, "subject").text = subject
#             ET.SubElement(student, "grade").text = grade
#             tree = ET.ElementTree(root)
#             file_path = os.path.join(settings.MEDIA_ROOT, f"{student_name}_{subject}.xml")
#             tree.write(file_path)

#             return redirect('list_xml')
#     else:
#         form = StudentPerformanceForm()
#     return render(request, 'performance/upload.html', {'form': form})

# def list_xml(request):
#     files = os.listdir(settings.MEDIA_ROOT)
#     if not files:
#         return HttpResponse("No XML files found.")
#     return render(request, 'performance/list.html', {'files': files})

# def upload_file(request):
#     if request.method == 'POST' and request.FILES['file']:
#         file = request.FILES['file']
#         file_path = os.path.join(settings.MEDIA_ROOT, file.name)
#         with open(file_path, 'wb+') as destination:
#             for chunk in file.chunks():
#                 destination.write(chunk)

#         # Проверка валидности XML-файла
#         try:
#             tree = ET.parse(file_path)
#             root = tree.getroot()
#         except ET.ParseError:
#             os.remove(file_path)
#             return HttpResponse("Invalid XML file.")

#         return redirect('list_xml')
#     return render(request, 'performance/upload_file.html')

# 
import xml.etree.ElementTree as ET
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from .forms import StudentPerformanceForm

def home(request):
    return render(request, 'performance/home.html')

def upload_xml(request):
    if request.method == 'POST':
        form = StudentPerformanceForm(request.POST)
        if form.is_valid():
            student_name = form.cleaned_data['student_name']
            subject = form.cleaned_data['subject']
            grade = form.cleaned_data['grade']

            # Сохранение данных в XML-файл
            root = ET.Element("root")
            student = ET.SubElement(root, "student")
            ET.SubElement(student, "name").text = student_name
            ET.SubElement(student, "subject").text = subject
            ET.SubElement(student, "grade").text = grade
            tree = ET.ElementTree(root)
            file_path = os.path.join(settings.MEDIA_ROOT, f"{student_name}_{subject}.xml")
            tree.write(file_path)

            return redirect('list_xml')
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
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Проверка валидности XML-файла
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            print(root)
        except ET.ParseError:
            os.remove(file_path)
            return HttpResponse("Invalid XML file.")

        return redirect('list_xml')
    
    return render(request, 'performance/uploud_file.html')


