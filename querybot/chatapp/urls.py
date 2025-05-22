from django.urls import path
from .views import chat_page, chat_view, upload_image

urlpatterns = [
    path("", chat_page, name="chat_page"),
    path("chat/", chat_view, name="chat_api"),
    path('upload-image/', upload_image, name='upload_image'),
]
