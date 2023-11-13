from django.shortcuts import render
import json  # Import the json module
from django.http import HttpResponse
from pymongo import MongoClient
from django.conf import settings

def store_video(request):
    connect_string = settings.MONGO_CONNECTION_STRING
    my_client = MongoClient(connect_string)

    # First define the database name
    dbname = my_client['Video']

    # Now get/create collection name
    collection_name = dbname["Set_of_videos"]

    if request.method == 'POST':
        # Get the JSON file from the request.FILES dictionary
        json_file = request.FILES.get('jsonFile', None)

        if json_file:
            try:
                # Parse the JSON content from the file
                json_content = json.loads(json_file.read().decode('utf-8'))

                # Insert the parsed JSON content into the collection
                collection_name.insert_one(json_content)

                return HttpResponse('JSON file uploaded successfully!', status=200)
            except json.JSONDecodeError as e:
                return HttpResponse(f'Error decoding JSON: {str(e)}', status=400)
        else:
            return HttpResponse('No JSON file provided!', status=400)
    else:
        return render(request, 'index.html')

