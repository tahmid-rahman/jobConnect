

from django.urls import path
from . import views

app_name = 'chatApp'

urlpatterns = [
    path('', views.index, name='index'),
    path('get_thread_updates/', views.get_thread_updates, name='get_thread_updates'),
    path('<int:thread_id>/', views.fetch_messages, name='fetch_messages'),
    path('send_message/', views.send_message, name='send_message'),
    path('delete_message/<int:msg_id>/', views.delete_message, name='delete_message'),
    path('edit_message/<int:msg_id>/', views.edit_message, name='edit_message'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('new_chat/', views.create_new_chat, name='create_new_chat'),
    path('new/<int:recipient_id>/', views.start_direct_chat, name='start_direct_chat'),
    path('get_unread_count/', views.get_unread_count, name='get_unread_count'),
]