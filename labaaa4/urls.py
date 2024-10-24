"""labaaa4 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from performance.views import home




urlpatterns = [
    path('admin/', admin.site.urls),
    path('performance/', include('performance.urls')),
    path('', home, name='home'),
] 
# Этот оператор проверяет, включен ли режим отладки. Если да, выполняется следующий блок кода.
if settings.DEBUG:
    # settings.MEDIA_URL: Это URL-адрес, по которому будут доступны загруженные медиафайлы. 
    # document_root=settings.MEDIA_ROOT: Это параметр функции static, который указывает на 
    # корневую директорию на сервере, где хранятся загруженные медиафайлы. 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)