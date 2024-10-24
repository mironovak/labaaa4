
import xml.etree.ElementTree as ET
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .forms import StudentPerformanceForm, DataSourceForm
from .models import StudentPerformance
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


#возвращает отрендеренный шаблон home.html, который находится в директории performance.
def home(request):
    return render(request, 'performance/home.html')

def upload_xml(request):
    #  Проверяет, является ли запрос POST-запросом.
    if request.method == 'POST':
        # Создает экземпляр формы StudentPerformanceForm с данными из POST-запроса.
        form = StudentPerformanceForm(request.POST)
        # Проверяет, являются ли данные формы корректными.
        if form.is_valid():
            # Извлекает данные из формы.
            student_name = form.cleaned_data['student_name']
            subject = form.cleaned_data['subject']
            grade = form.cleaned_data['grade']
            save_to = form.cleaned_data['save_to']

            # Проверяет, нужно ли сохранить данные в файл.
            if save_to == 'file':
                # Создает корневой элемент XML.
                root = ET.Element("root")
                # Создает дочерний элемент student внутри корневого элемента.
                student = ET.SubElement(root, "student")
                # Создает дочерний элемент name внутри student и устанавливает его текстовое значение.
                ET.SubElement(student, "name").text = student_name
                ET.SubElement(student, "subject").text = subject
                ET.SubElement(student, "grade").text = grade
                # Создает дерево XML.
                tree = ET.ElementTree(root)
                # Формирует путь к файлу.
                file_path = os.path.join(settings.MEDIA_ROOT, f"{student_name}_{subject}.xml")
                # Записывает дерево XML в файл.
                tree.write(file_path)
            # Проверяет, нужно ли сохранить данные в базу данных.
            elif save_to == 'db':
                # Проверяет, существует ли дублирующая запись в базе данных.
                if StudentPerformance.is_duplicate(student_name, subject, grade):
                    # Возвращает HTTP-ответ, если найдена дублирующая запись.
                    return HttpResponse("Найдена дублирующая запись. Не сохранено в базу данных.")
                # Создает новую запись в базе данных.
                StudentPerformance.objects.create(student_name=student_name, subject=subject, grade=grade)
            # Перенаправляет на URL-адрес list_data.
            return redirect('list_data')  
    else:
        #  Создает пустую форму.
        form = StudentPerformanceForm()
    #  Возвращает отрендеренный шаблон upload.html с формой.   
    return render(request, 'performance/upload.html', {'form': form})

def list_xml(request):
    # Проверяет, существует ли директория MEDIA_ROOT.
    if not os.path.exists(settings.MEDIA_ROOT):
        # Создает директорию MEDIA_ROOT, если она не существует.
        os.makedirs(settings.MEDIA_ROOT)
    # Получает список файлов в директории MEDIA_ROOT.
    files = os.listdir(settings.MEDIA_ROOT)
    # Проверяет, пуст ли список файлов.
    if not files:
        # Возвращает HTTP-ответ, если файлы не найдены.
        return HttpResponse("No XML files found.")
    # Возвращает отрендеренный шаблон list.html с переданным списком файлов.
    return render(request, 'performance/list.html', {'files': files})


def upload_file(request):
    # Здесь проверяется, является ли метод запроса POST. 
    if request.method == 'POST':
        # Проверяется, есть ли в загруженных файлах (в request.FILES) файл с ключом 'file'. 
        # Если файл загружен, код внутри этого блока будет выполнен.
        if 'file' in request.FILES:
            # Если файл существует, он извлекается из request.FILES и сохраняется в переменной file.
            file = request.FILES['file']
            # Создается полный путь для сохранения файла. settings.MEDIA_ROOT - это директория на сервере, 
            # куда будут загружаться файлы. file.name - это имя загруженного файла.
            file_path = os.path.join(settings.MEDIA_ROOT, file.name)

            # Открывается файл по указанному пути для записи в бинарном режиме ('wb+'). 
            # Это позволяет записывать данные в файл.
            with open(file_path, 'wb+') as destination:
                # Файл загружается по частям (чанками). Метод file.chunks() позволяет обрабатывать файл по частям, 
                # что полезно для больших файлов. 
                # Каждая часть записывается в открытый файл.
                for chunk in file.chunks():
                    destination.write(chunk)

            # После завершения записи проверяется, существует ли файл по указанному пути. 
            # Если нет, возвращается HTTP-ответ с сообщением об ошибке.
            # os.path.exists — это метод в Python, который используется для 
            # проверки существования указанного пути в файловой системе. 
            if not os.path.exists(file_path):
                # Это форматированная строка (f-string) в Python, которая позволяет включать переменные в строку. 
                # Выражение {file_path} будет заменено значением переменной file_path, 
                # которая содержит путь к файлу, который пытались получить.
                return HttpResponse(f"File not found: {file_path}")

            # Этот блок используется для обработки исключений.
            try:
                # parse - тот метод загружает и разбирает XML-файл по указанному пути (file_path) и возвращает объект дерева XML 
                # (объект типа ElementTree), 
                # который сохраняется в переменной tree.
                tree = ET.parse(file_path)
                # Метод getroot() возвращает корневой элемент дерева XML.
                root = tree.getroot()
                print(root)
            # Этот блок перехватывает исключения типа ParseError, которые могут возникнуть, если файл не является корректным 
            # XML-документом. 
            # Переменная e будет содержать информацию об ошибке.
            # except - ошибки из try
            # ParseError - класс исключений возникает, когда происходит ошибка при разборе (парсинге) XML-документа. 
            except ET.ParseError as e:
                # файл удаляется, чтобы избежать хранения проблемного файла.
                os.remove(file_path)
                # Выводит сообщение об неожиданной ошибке на консоль для отладки.
                print(f"XML parsing error: {e}")
                # Возвращает HTTP-ответ с сообщением о том, что загруженный файл некорректен (невалидный XML)
                return HttpResponse("Invalid XML file.")
            # перехватывает любые другие исключения, которые могут возникнуть. 
            # Это более общий случай, который позволяет обработать неожиданные ошибки.
            except Exception as e:
                # файл удаляется, чтобы избежать хранения проблемного файла.
                os.remove(file_path)
                # Выводит сообщение об неожиданной ошибке на консоль для отладки.
                print(f"Unexpected error: {e}")
                # Возвращает HTTP-ответ с сообщением о том, что произошла неожиданная ошибка. 
                return HttpResponse("An unexpected error occurred.")
            # Если парсинг прошел успешно и не возникло ошибок, происходит перенаправление на другую страницу 
            # Функция redirect() отправляет HTTP 302 ответ с указанием нового URL.
            return redirect('list_xml')
        else:
            # Этот блок выполняется, если в запросе не было загруженного файла.
            return HttpResponse('No file was uploaded')
    # Функция render() создает HTTP-ответ с содержимым указанного шаблона.    
    return render(request, 'performance/upload_file.html')


# pk: Параметр, представляющий первичный ключ (primary key) объекта, который мы хотим редактировать. 
def edit_db(request, pk):
    # Проверка на метод запроса. 
    if request.method == 'POST':
        # .objects.get(pk=pk): Метод get() используется для получения единственного объекта из базы данных по его 
        # первичному ключу (pk). 
        # Если объект не найден, будет вызвано исключение DoesNotExist.
        student = StudentPerformance.objects.get(pk=pk)
        # request.POST: Передается данные формы, отправленные пользователем. Это словарь с данными полей формы.
        form = StudentPerformanceForm(request.POST)
        # Метод is_valid() проверяет, корректны ли данные формы. Если данные валидны
        if form.is_valid():
            # form.cleaned_data: Это атрибут формы, который содержит очищенные и валидированные данные из формы. 
            student.student_name = form.cleaned_data['student_name']
            student.subject = form.cleaned_data['subject']
            student.grade = form.cleaned_data['grade']
            # Метод save() сохраняет изменения в объекте student обратно в базу данных. 
            student.save()
            # Функция redirect() перенаправляет пользователя на другую страницу после успешного сохранения изменений. 
            return redirect('list_db')
    else:
        #  получаем объект студента из базы данных по его первичному ключу.
        student = StudentPerformance.objects.get(pk=pk)
        # Здесь создается экземпляр формы с начальными значениями. Параметр initial задает начальные значения для
        # полей формы на основе текущих значений объекта студента. 
        # Это позволяет пользователю увидеть текущие данные в форме для редактирования.
        form = StudentPerformanceForm(initial={'student_name': student.student_name, 'subject': student.subject, 'grade': student.grade})
    # Функция render() создает HTTP-ответ с содержимым указанного шаблона   
    # {'form': form}: Передает форму в контекст шаблона.  
    return render(request, 'performance/edit.html', {'form': form})

def delete_db(request, pk):
    # .objects.get(pk=pk): Метод get() используется для получения единственного объекта из базы данных по его 
    #  первичному ключу (pk). 
    #  Если объект не найден, будет вызвано исключение DoesNotExist.
    student = StudentPerformance.objects.get(pk=pk)
    if request.method == 'POST':
        # Это удаляет запись студента из базы данных. 
        student.delete()
        # redirect() перенаправляет пользователя на другую страницу после успешного удаления.
        return redirect('list_db')
    # {'student': student}: Передает объект студента в контекст шаблона.
    return render(request, 'performance/delete_db.html', {'student': student})

def list_db(request):
    #  Метод all() возвращает QuerySet, содержащий все объекты модели StudentPerformance
    students = StudentPerformance.objects.all()
    # render(): Функция, которая создает HTTP-ответ с содержимым указанного шаблона.
    # request: Передается объект запроса для корректной обработки.
    # {'students': students}: Передает список студентов в контекст шаблона. 
    return render(request, 'performance/list_db.html', {'students': students})

def list_data(request):
    if request.method == 'POST':
        # форма используется для валидации и обработки выбора источника данных.
        # request.POST: Передаются данные формы, отправленные пользователем. Это словарь с данными полей формы.
        form = DataSourceForm(request.POST)
        # Метод is_valid() проверяет, корректны ли данные формы. 
        if form.is_valid():
            # form.cleaned_data: Это атрибут формы, который содержит очищенные и валидированные данные из формы. 
            # Здесь мы извлекаем значение поля source, 
            # которое указывает на выбранный источник данных (файл или база данных).
            source = form.cleaned_data['source']
            # Если выбранный источник — файл ('file'), 
            # происходит перенаправление на страницу списка XML-файлов с помощью функции redirect(). 'list_xml'
            if source == 'file':
                return redirect('list_xml')
            # Если выбранный источник — база данных ('db'), происходит перенаправление на страницу списка студентов ('list_db').
            elif source == 'db':
                return redirect('list_db')
    else:
        # создается новый экземпляр формы без предварительно заполненных данных.
        form = DataSourceForm()
    # {'form': form}: Передает форму в контекст шаблона. 
    return render(request, 'performance/list_data.html', {'form': form})
 

def search_page(request):
    return render(request, 'performance/search.html')

# @csrf_exempt: Декоратор Django, который отключает защиту от подделки межсайтовых запросов     
@csrf_exempt
def search_db(request):
    # request.GET: Атрибут объекта запроса, который содержит параметры запроса, переданные через метод GET. 
    # Метод get() используется для извлечения значения параметра с именем 'query'
    query = request.GET.get('query', '')
    
    # Метод filter() используется для фильтрации объектов модели на основе заданных условий. 
    if query:
        students = StudentPerformance.objects.filter(
            # Q-позволяет создавать сложные запросы с использованием логических операторов
            # student_name__icontains=query: Проверяет, содержится ли подстрока query в поле student_name
            # subject__icontains=query: Проверяет, содержится ли подстрока query в поле subject.
            Q(student_name__icontains=query) | Q(subject__icontains=query)
        )
    else:
        # выбираются все объекты модели StudentPerformance. Метод all() возвращает QuerySet со всеми записями в таблице.
        students = StudentPerformance.objects.all()
# Создается список словарей с использованием генератора списков. Для каждого объекта student в наборе 
# результатов (students) создается словарь с тремя ключами:
    results = [
        {
            'name': student.student_name, 
            'subject': student.subject,
            'grade': student.grade
        }
        for student in students
    ]
    
    return JsonResponse({'results': results})
