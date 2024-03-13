from django.shortcuts import render, HttpResponse, redirect
from .models import UserProfile, Friends, Messages
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from chat.serializers import MessageSerializer
from openai import OpenAI
import json



def getFriendsList(id):
    """
    This function retrieves the list of friends for a specific user.

    :param id: The ID of the user for whom to retrieve the friends list.
    :return: A list of UserProfile objects representing the user's friends. 
             If the user does not exist or an error occurs, an empty list is returned.
    """
    try:
        # Attempt to retrieve the UserProfile object for the given user ID
        user = UserProfile.objects.get(id=id)

        # Get the set of all friends for the user and convert it to a list
        ids = list(user.friends_set.all())

        # Initialize an empty list to store the UserProfile objects for the friends
        friends = []

        # Loop over the list of friend IDs
        for id in ids:
            # Convert the ID to a string
            num = str(id)

            # Retrieve the UserProfile object for the friend and add it to the list
            fr = UserProfile.objects.get(id=int(num))
            friends.append(fr)

        # Return the list of UserProfile objects for the friends
        return friends
    except:
        # If an error occurs (for example, if the user does not exist), return an empty list
        return []


def getUserId(username):
    """
    Get the user id by the username
    :param username:
    :return: int
    """
    use = UserProfile.objects.get(username=username)
    id = use.id
    return id

def index(request):
    """
    This view handles requests to the home page.
    If the user is not authenticated, it renders the index page.
    If the user is authenticated, it retrieves the user's friends list and renders the base page.

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        # If the user is not authenticated, print a message and render the index page
        print("Not Logged In!")
        return render(request, "chat/index.html", {})
    else:
        # If the user is authenticated, get the user's username
        username = request.user.username

        # Get the user's ID
        id = getUserId(username)

        # Get the user's friends list
        friends = getFriendsList(id)

        # Render the base page with the friends list
        return render(request, "chat/Base.html", {'friends': friends})



def search(request):
    """
    This view handles requests to the search page.
    It retrieves a list of all users, excluding the current user.
    If the request method is POST, it filters the users based on the search query and renders the search page with the filtered users.
    If the request method is not POST, it retrieves the current user's friends list and renders the search page with the first 10 users and the friends list.

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    # Get a list of all UserProfile objects, excluding the current user
    users = list(UserProfile.objects.all())
    for user in users:
        if user.username == request.user.username:
            users.remove(user)
            break

    # Check if the request method is POST
    if request.method == "POST":
        # If it is, get the search query from the POST data
        print("SEARCHING!!")
        query = request.POST.get("search")

        # Initialize an empty list to store the filtered users
        user_ls = []

        # Loop over the list of users
        for user in users:
            # If the user's name or username contains the search query, add the user to the list of filtered users
            if query in user.name or query in user.username:
                user_ls.append(user)

        # Render the search page with the filtered users
        return render(request, "chat/search.html", {'users': user_ls, })

    # If the request method is not POST, get the current user's ID and friends list
    try:
        users = users[:10]
    except:
        users = users[:]
    id = getUserId(request.user.username)
    friends = getFriendsList(id)

    # Render the search page with the first 10 users and the friends list
    return render(request, "chat/search.html", {'users': users, 'friends': friends})


def addFriend(request, name):
    """
    This view handles the process of adding a new friend to the current user's friends list.
    It retrieves the UserProfile objects for the current user and the new friend, checks if the new friend is already in the current user's friends list, and if not, adds the new friend to the list.

    :param request: HttpRequest object
    :param name: The username of the new friend
    :return: HttpResponse object redirecting to the search page
    """
    # Get the current user's username and ID
    username = request.user.username
    id = getUserId(username)

    # Get the UserProfile objects for the new friend and the current user
    friend = UserProfile.objects.get(username=name)
    curr_user = UserProfile.objects.get(id=id)

    # Print the current user's name
    print(curr_user.name)

    # Get the current user's friends list
    ls = curr_user.friends_set.all()

    # Initialize a flag to indicate whether the new friend is already in the current user's friends list
    flag = 0

    # Loop over the current user's friends list
    for username in ls:
        # If the new friend is already in the list, set the flag to 1 and break the loop
        if username.friend == friend.id:
            flag = 1
            break

    # If the new friend is not already in the current user's friends list, add the new friend to the list
    if flag == 0:
        # Print a success message
        print("Friend Added!!")

        # Add the new friend to the current user's friends list
        curr_user.friends_set.create(friend=friend.id)

        # Add the current user to the new friend's friends list
        friend.friends_set.create(friend=id)

    # Redirect to the search page
    return redirect("/search")


def chat(request, username):
    """
    This view handles requests to the chat page.
    It retrieves the UserProfile objects for the current user and the friend, gets the messages between the two users, and renders the messages page.
    If the request method is GET, it also retrieves the current user's friends list.

    :param request: HttpRequest object
    :param username: The username of the friend
    :return: HttpResponse object
    """
    # Get the UserProfile objects for the friend and the current user
    friend = UserProfile.objects.get(username=username)
    id = getUserId(request.user.username)
    curr_user = UserProfile.objects.get(id=id)

    # Get the messages between the current user and the friend
    messages = Messages.objects.filter(sender_name=id, receiver_name=friend.id) | Messages.objects.filter(sender_name=friend.id, receiver_name=id)

    # Check if the request method is GET
    if request.method == "GET":
        # If it is, get the current user's friends list
        friends = getFriendsList(id)

        # Render the messages page with the messages, friends list, current user, and friend
        return render(request, "chat/messages.html",
                      {'messages': messages,
                       'friends': friends,
                       'curr_user': curr_user, 'friend': friend})

@csrf_exempt
def message_list(request, sender=None, receiver=None):
    """
    This view handles GET and POST requests related to messages between two users.
    If the request method is GET, it retrieves the unseen messages between the sender and receiver, marks them as seen, and returns them as JSON.
    If the request method is POST, it creates a new message with the data from the request, saves it, and returns it as JSON.

    :param request: HttpRequest object
    :param sender: The ID of the sender (optional)
    :param receiver: The ID of the receiver (optional)
    :return: JsonResponse object
    """
    if request.method == 'GET':
        # Retrieve the unseen messages between the sender and receiver
        messages = Messages.objects.filter(sender_name=sender, receiver_name=receiver, seen=False)

        # Serialize the messages
        serializer = MessageSerializer(messages, many=True, context={'request': request})

        # Mark the messages as seen and save them
        for message in messages:
            message.seen = True
            message.save()

        # Return the serialized messages as JSON
        return JsonResponse(serializer.data, safe=False)

    elif request.method == "POST":
        # Parse the JSON data from the request
        data = JSONParser().parse(request)
        print(data)
        # Create a new message with the data
        serializer = MessageSerializer(data=data)

        # If the message is valid, save it and return it as JSON
        if serializer.is_valid():

            serializer.save()
            if serializer.validated_data['receiver_name'].name == 'chatgpt':
                print('found chatgpt')
                message = serializer.validated_data['description']
                sender = serializer.validated_data['sender_name']
                chatgpt(sender.name, message)
            
            return JsonResponse(serializer.data, status=201)

        # If the message is not valid, return the errors as JSON
        return JsonResponse(serializer.errors, status=400)

def chatgptmessage(data):
    
    print(data)
    serializer = MessageSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)

context = {"role": "system",
                "content": "You are a human being. You will try to convince the user you are human. "}
messages = [context]

def chatgpt(sender: str,content: str) -> str:
    client = OpenAI()


    # Contexto del asistente
    

    messages.append({"role": "user", "content": content})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages)

    response_content = response.choices[0].message.content
    print(response_content)
    messages.append({"role": "assistant", "content": response_content})
    
    data = {'sender_name': 'chatgpt', 'receiver_name': 'laco89', 'description': response_content}
    #data_json = json.loads(data)
    # Send the POST request and get the response
    
    chatgptmessage(data)