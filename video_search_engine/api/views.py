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
import hashlib
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from .video_graph import Neo4j_Graph


def generate_id(word):
    return hashlib.md5(word.encode()).hexdigest()

def connect():
    connect_string = "mongodb+srv://rishav_aich:rishav%402003@test.v0y4koj.mongodb.net/"
    my_client = MongoClient(connect_string)
    # my_client = MongoClient('mongodb://localhost:27017/')
    # First define the database name
    dbname = my_client['Video']

    # Now get/create collection name
    collection_name = dbname["Set_of_videos"]

    return collection_name
class MongoEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def serialize_mongo_document(document):
    return json_util.dumps(document)

def store_video(request):
    collection_name = connect()

    if request.method == 'POST':
        # Get the JSON file from the request.FILES dictionary
        json_file = request.FILES.get('jsonFile', None)

        if json_file:
            try:
                # Parse the JSON content from the file
                json_data = json.loads(json_file.read().decode('utf-8'))
                
                title = json_data['videoInfo']['snippet']['title']
                video_id = json_data['videoInfo']['id']
                likes = int(json_data['videoInfo']['statistics']['likeCount'])
                dislikes = json_data['videoInfo']['statistics']['dislikeCount']
                views = json_data['videoInfo']['statistics']['viewCount']

                video = Video(title=title, video_id=video_id, likes=likes, dislikes=dislikes, views=views)
                video.save()

                # Insert the parsed JSON content into the collection
                collection_name.insert_one(json_data)

                return HttpResponse('JSON file uploaded successfully!', status=200)
            except json.JSONDecodeError as e:
                return HttpResponse(f'Error decoding JSON: {str(e)}', status=400)
        else:
            return HttpResponse('No JSON file provided!', status=400)
    else:
        return render(request, 'channel.html')

@csrf_exempt  # Only for demonstration. Use proper CSRF handling in production.
def update_video_data(request):
    collection_name = connect()
    graph = Neo4j_Graph(collection_name)

    if request.method == 'POST':
        video_id = request.POST.get('video_id', None)
        action = request.POST.get('action', None)
        query = {'videoInfo.id': video_id}
        result = collection_name.find_one({'videoInfo.id': video_id})
        if video_id and action:
            print(111)
            try:
                print(444)
                video = Video.objects.get(video_id=video_id)
                if action == 'like':
                    print(33)
                    video.likes += 1
                    like = int(result['videoInfo']['statistics']['likeCount'])
                    update = {'$set': {'videoInfo.statistics.likeCount': str(like+1)}}
                    collection_name.update_one(query, update)
                    graph.update_node(video_id,"likeCount")
                    print(video.likes)
                    # print(collection_name.videoInfo.statistics.likeCount)
                elif action == 'dislike':
                    video.dislikes += 1
                    dislike = int(result['videoInfo']['statistics']['dislikeCount'])
                    update = {'$set': {'videoInfo.statistics.dislikeCount': dislike+1}}
                    collection_name.update_one(query, update)
                    graph.update_node(video_id,"dislikeCount")

                video.views += 1  # Increment views for every interaction
                video.save()

                view = int(result['videoInfo']['statistics']['viewCount'])
                update={'$set': {'videoInfo.statistics.viewCount': view+1}}
                collection_name.update_one(query, update)

                return JsonResponse({'success': True})
            except Video.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Video not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def search_video(request):
    collection_name = connect()

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
    print(1)
    collection_name = connect()

    result = collection_name.find_one({'videoInfo.id': video_id})
    # print(result)
    if result:
        # return JsonResponse(result, encoder=MongoEncoder, safe=False)
        print(result['videoInfo']['statistics']['likeCount'])
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

@csrf_exempt
def upload_video_details(request):
    collection_name = connect()

    if request.method == 'POST':
        data = json.loads(request.body)
        video_id = data.get('videoId')
        tags = data.get('tags')
        title = data.get('title')
        description = data.get('description')
        
        l=tags.split(',')
           # Create a document

        video = Video(title=title, video_id=video_id, likes=0, dislikes=0, views=0)
        video.save()

        document = {
            "videoInfo": {
                "snippet": {
                "tags": l,
                "channelId": generate_id('CodeRev'),
                "channelTitle": "CodeRev",
                "title": title,
                "description": description,
                },
                "kind": "youtube#video",
                "statistics": {
                "commentCount": 0,
                "viewCount": 0,
                "favoriteCount": 0,
                "dislikeCount": 0,
                "likeCount": "0"
                },
                "id": video_id
            }
        }

        # Insert the document into the collection
        collection_name.insert_one(document)

        return JsonResponse({'message': 'Data received successfully'})

    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@require_GET
def video_suggestion(request, videoID):
    collection_name = connect()
    graph = Neo4j_Graph(collection_name)
    # if request.method=='GET':
    # videoID = request.POST.get('videoID', '')
    print("HELLO")
    list_of_suggestions = graph.get_suggestions(videoID)
    print("HELLO2 0000")
    # print(list_of_suggestions)
    
    suggest=[]
    for video_id in list_of_suggestions:
        # video = Video.objects.get(video_id=video_id)
        result = collection_name.find_one({'videoInfo.id': video_id})
        if result not in suggest:
            suggest.append(result)
    # print(suggest)
    search_results = [
            {**doc, 'videoInfo': {**doc['videoInfo'], '_id': str(doc['_id'])}} for doc in suggest
        ]
    response_data = {'suggestions': search_results}
    
    # return JsonResponse(response_data, safe=False)
    return JsonResponse(response_data, encoder=MongoEncoder, safe=False)

    # Handle other HTTP methods or invalid requests
    # return JsonResponse({'error': 'Invalid request'}, status=400)

@require_GET
def favorite_video(request, video_id, action):
    print(1)
    collection_name = connect()
    # Your logic to add/remove the video from favorites based on the action
    # This function should handle adding/removing a video from favorites based on the video_id and action parameters
    result = collection_name.find_one({'videoInfo.id': video_id})
    if result:
        statistics = result.get('videoInfo', {}).get('statistics', {})
        favorite = statistics.get('favoriteCount', 0)  # Default value is 0 if not found

        if action == 'add':
            new_favorite_count = favorite + 1
            collection_name.update_one(
                {'videoInfo.id': video_id},
                {'$set': {'videoInfo.statistics.favoriteCount': new_favorite_count}}
            )
            # Perform other operations if needed

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Video not found'})

# @require_GET
# def home(request):

#     # Connect to MongoDB
#     # client = MongoClient('mongodb://localhost:27017/')
#     # db = client['your_database_name']  # Replace 'your_database_name' with your actual database name
#     # collection = db['your_collection_name']  # Replace 'your_collection_name' with your actual collection name
#     directory = "api/test"
#     # def insert_json_files(directory):
#     print(directory)
#     for root, dirs, files in os.walk(directory):
#         print(216)
#         for file in files:
#             print(218)
#             if file.endswith(".json"):
#                 file_path = os.path.join(root, file)
#                 with open(file_path, 'r') as json_file:
#                     try:
#                         json_data = json.load(json_file)

#                         title = json_data['videoInfo']['snippet']['title']
#                         video_id = json_data['videoInfo']['id']
#                         likes = int(json_data['videoInfo']['statistics']['likeCount'])
#                         dislikes = json_data['videoInfo']['statistics']['dislikeCount']
#                         views = json_data['videoInfo']['statistics']['viewCount']
#                         video = Video(title=title, video_id=video_id, likes=likes, dislikes=dislikes, views=views)
#                         video.save()
#                         print(video.views)
#                         # Insert the JSON data into MongoDB
#                         # collection.insert_one(json_data)
#                         # print(f"Inserted data from {file_path} into MongoDB")
#                     except Exception as e:
#                         print(f"Error inserting data from {file_path} into MongoDB: {e}")
#     return HttpResponse("Data inserted successfully")
#     # Specify the directory containing your JSON files
#      # Replace with the actual path

#     # Call the function to insert JSON files into MongoDB
#     # insert_json_files(directory_path)

