from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_xml, name='upload_xml'),
    path('list/', views.list_xml, name='list_xml'),
    path('upload_file/', views.upload_file, name='upload_file'),
]
