from django.shortcuts import render
from django.http import JsonResponse
import json  # Import the json module
from django.http import HttpResponse
from pymongo import MongoClient
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Video
from json import JSONEncoder
from django.core.serializers.json import DjangoJSONEncoder
from bson.objectid import ObjectId
from django.views.decorators.http import require_GET, require_POST
from bson import json_util


class MongoEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def serialize_mongo_document(document):
    return json_util.dumps(document)

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
                
                title = json_content['videoInfo']['snippet']['title']
                video_id = json_content['videoInfo']['id']
                likes = int(json_content['videoInfo']['statistics']['likeCount'])
                dislikes = json_content['videoInfo']['statistics']['dislikeCount']
                views = json_content['videoInfo']['statistics']['viewCount']

                video = Video(title=title, video_id=video_id, likes=likes, dislikes=dislikes, views=views)
                video.save()

                # Insert the parsed JSON content into the collection
                collection_name.insert_one(json_content)

                return HttpResponse('JSON file uploaded successfully!', status=200)
            except json.JSONDecodeError as e:
                return HttpResponse(f'Error decoding JSON: {str(e)}', status=400)
        else:
            return HttpResponse('No JSON file provided!', status=400)
    else:
        return render(request, 'index.html')

@csrf_exempt  # Only for demonstration. Use proper CSRF handling in production.
def update_video_data(request):
    connect_string = settings.MONGO_CONNECTION_STRING
    my_client = MongoClient(connect_string)

    # First define the database name
    dbname = my_client['Video']

    # Now get/create collection name
    collection_name = dbname["Set_of_videos"]

    if request.method == 'POST':
        video_id = request.POST.get('video_id', None)
        action = request.POST.get('action', None)
        query = {'videoInfo.id': video_id}
        if video_id and action:
            try:
                video = Video.objects.get(video_id=video_id)
                if action == 'like':
                    video.likes += 1
                    update = {'$set': {'videoInfo.statistics.likeCount': str(video.likes)}}
                    collection_name.update_one(query, update)
                    print(video.likes)
                    print(collection_name.videoInfo.statistics.likeCount)
                elif action == 'dislike':
                    video.dislikes += 1
                    update = {'$set': {'videoInfo.statistics.dislikeCount': video.dislikes}}
                    collection_name.update_one(query, update)
                video.views += 1  # Increment views for every interaction
                video.save()

                update={'$set': {'videoInfo.statistics.viewCount': video.views}}
                collection_name.update_one(query, update)

                return JsonResponse({'success': True})
            except Video.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Video not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def search_video(request):
    connect_string = settings.MONGO_CONNECTION_STRING
    my_client = MongoClient(connect_string)

    # First define the database name
    dbname = my_client['Video']

    # Now get/create collection name
    collection_name = dbname["Set_of_videos"]

    if request.method == 'POST':
        query = request.POST.get('query', '')
        result = collection_name.find({
            "$or": [
                {"videoInfo.snippet.title": {"$regex": f".*{query}.*", "$options": "i"}},
                {"videoInfo.snippet.description": {"$regex": f".*{query}.*", "$options": "i"}},
                {"videoInfo.snippet.tags": {"$regex": f".*{query}.*", "$options": "i"}}
            ]
        })
        
        # video_ids = [doc['videoInfo']['id'] for doc in result]
        search_results = [
            {**doc, 'videoInfo': {**doc['videoInfo'], '_id': str(doc['_id'])}} for doc in result
        ]

        response_data = {
            'query': query,
            'results': search_results,
        }

        # video_information_dict = {}
        # for video in video_ids:
        #     information=Video.objects.get(video_id=video)
        #     video_information_dict[video] = [information.likes, information.dislikes, information.views]

        return JsonResponse(response_data, encoder=MongoEncoder, safe=False)

    return render(request, 'youtube.html')

@require_GET
def get_video_data(request, video_id):
    connect_string = settings.MONGO_CONNECTION_STRING
    my_client = MongoClient(connect_string)

    # First define the database name
    dbname = my_client['Video']

    # Now get/create collection name
    collection_name = dbname["Set_of_videos"]

    result = collection_name.find_one({'videoInfo.id': video_id})
    print(result)
    if result:
        # return JsonResponse(result, encoder=MongoEncoder, safe=False)
        video_data = {
            'videoInfo': {
                'id': result['videoInfo']['id'],
                'snippet': result['videoInfo']['snippet'],
                'statistics': result['videoInfo']['statistics'],
            }
            # Add more fields as needed
        }
        return JsonResponse({'success': True, 'videoData': video_data})
    else:
        return JsonResponse({'error': 'Video not found'}, status=404)
