

from django.urls import path
from . import views
from .views import upload_file, search_text, search_page

urlpatterns = [
    path('upload/', views.upload_xml, name='upload_xml'),
    path('list/', views.list_xml, name='list_xml'),
    path('upload_file/',upload_file, name='upload_file'),
    path('search_db/', views.search_db, name='search_db'),
    path('edit_db/<int:pk>/', views.edit_db, name='edit_db'),
    path('delete_db/<int:pk>/', views.delete_db, name='delete_db'),
    path('list_db/', views.list_db, name='list_db'),
    path('list_data/', views.list_data, name='list_data'),
    path('search_text/', search_text, name='search_text'),
    path('search/', search_page, name='search_page'),
]
