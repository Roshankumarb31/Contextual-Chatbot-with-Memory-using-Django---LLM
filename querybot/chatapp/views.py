from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
from time import sleep
from django.conf import settings
from .chat_sesesion import get_chat_response
from .chat_logic import get_chat_response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
from .find_similars import find_similar_properties



def chat_page(request):
    request.session.pop("entity_memory", None)
    return render(request, "chat.html")

@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_input = data.get("message", "")

        response_text, is_tableview = get_chat_response(user_input, request.session)

        print(f"###   {is_tableview}   ###")

        if not is_tableview:
            print(response_text)

            return JsonResponse({"response": response_text})
        
        else:
            static_json_dir = os.path.join(settings.BASE_DIR, 'static', 'json')
            os.makedirs(static_json_dir, exist_ok=True)
            file_path = os.path.join(static_json_dir, 'data.json')
            with open(file_path, "r") as file:
                data = json.load(file)
                print("hii")
            return JsonResponse({"response": response_text, "data": data})

    return JsonResponse({"message": "Welcome to the chatbot"})


@csrf_exempt
def upload_image(request):
    if request.method == "POST" and request.FILES.get('image'):
        image = request.FILES['image']
        image_name = image.name
        upload_dir = os.path.join(settings.BASE_DIR, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        image_path = os.path.join(upload_dir, image_name)

        with open(image_path, 'wb') as img_file:
            for chunk in image.chunks():
                img_file.write(chunk)
        
        similar_properties = find_similar_properties(image_path)
        print(similar_properties)

        return JsonResponse({
            "response": "These are the similar properties for the uploaded image!!!",
            "properties": similar_properties
        })

    return JsonResponse({"result": {"status": "No image provided"}})