from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Room, Topic, Message, User
from .forms import RoomForm, MessageForm, UserForm, MyUserCreationForm
from django.db.models import Count
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

# Create your views here.

# rooms = [
#     {'id':1, 'name': "Lets learn python!"},
#     {'id':2, 'name': "Lets learn System design!"},
#     {'id':3, 'name': "Learn GO!"}
# ]


# creating view for login-registration page
def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            # we're trying flash messages here, there are in the sessions ande they're only stored until 1 browser refresh
            messages.error(request, 'User Does not exist')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user) #this login will add that user session to DB and also in cookies
            return redirect('home')
        else:
            messages.error(request, 'username or Password does not exist')
    context={'page':page}
    return render(request, 'base/login_register.html', context)

def logout_user(request):
    logout(request) # this method deletes token hence deletes the user
    return redirect('home')
    
def register_user(request):
    form = MyUserCreationForm
    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # this is to say that, hey check if its valid, if so currently freeze, why? coz to CLEAN DATA: ensure consistency in storing like if they capitalised name or full lower case something like that
            
            user.username = user.username.lower()
            user.save()
            login(request, user=user)
            return redirect('home')
        else:
            messages.error(request, 'Could not register user, error!')
    context = {'form':form}
    return render(request, 'base/login_register.html', context)



def home(request):
    
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)) # here we will use a Q function 
    room_count = rooms.count()

    # topics = Topic.objects.all() all the topics will be listed, but later change it to those topics which have highest number of rooms
    '''
    SQL: SELECT room.topic FROM room GROUP BY room.topic ORDER BY count(room.id) DESC;
    '''
    topics = Topic.objects.annotate(room_count=Count("room")).order_by('-room_count')[:5] #room means the model Room
    
    # now we're adding recent activities
    participant_messages = Message.objects.filter(Q(room__topic__name__icontains=q)).order_by('-created')
    context = {'rooms': rooms, 'topics':topics, 'room_count':room_count, 'activities':participant_messages} #this is for passing data to my response
    return render(request, 'base/home.html', context)

# Read
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.messages.all().order_by('-created') #reverse fk used here
    '''Note: here messages are stored in message, but room is a fk in msg, so access all msg based on room is what we're trying to say'''
    participants = room.participants.all()
    
    
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        
        room.participants.add(request.user)
        # if we dont do this also, the page will work, but problem is the post without any redirect operation may result in some complications
        return redirect('room',pk=room.id)
        
    context = {'room': room, 'room_messages':room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)



def user_profile(request, pk):
    user = User.objects.get(id=pk)
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    rooms = user.room_set.all() #passing only user's rooms
    context = {'user':user, 
               'rooms':rooms,
               'room_messages':room_messages, 
               'topics': topics, 
               'activities': room_messages
            }
    return render(request, 'base/profile.html', context)



# CRUD ON ROOMS 

# Create Room only if user is logged in
@login_required(login_url='login') #if a user is not logged in then he will be redirected to login
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
        
    if request.method == 'POST':
        # form = RoomForm(request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        
        # we're not saving this using the conventional is_valid coz we have made a change to add a new topic if a topic is not found
        
        # if form.is_valid():
        #     room = form.save(commit=False) # so this gives the instance of a room
        #     room.host = request.user
        #     room.save()
        
        return redirect('home')
        
    
    context = {'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

# Update Room

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) #means hey prefill this form with the instance of room
    topics = Topic.objects.all()
    
    # if a user is not the creater of that room, he should not delete the room
    if request.user != room.host:
        return HttpResponse("You're not authorised to update this room")
        
    if request.method=="POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.topic = topic
        room.save()
        return redirect('home')
        
        
        
    
    context = {'form':form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)

# Delete Room
@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You're not authorised to delete this room")
        
    if request.method == 'POST': #coz we click on confirm
        room.delete()
        return redirect('home')
    context  = {'obj':room, 'obj_type': room._meta.verbose_name}
    return render(request, 'base/delete.html', context)


# Delete message
@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("You're not authorised to delete this message")
        
    if request.method == 'POST': #coz we click on confirm
        message.delete()
        return redirect('home')
    context = {'obj': message, 'obj_type': message._meta.verbose_name}
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def edit_message(request, pk):
    # change this later to inhouse
    message = Message.objects.get(id=pk)
    form = MessageForm(instance=message)
    if request.user != message.user:
        return HttpResponse("You're not authorised to delete this message")
    
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message) 
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html', context)



# Update user-profile
@login_required(login_url='login')
def update_user(request):
    # the user is already logged in so no need to pass pk
    
    user = request.user
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
        
    
    context = {'form':form}
    return render(request, 'base/update-user.html', context)


def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request,'base/topics.html',context)

def activities_page(request):
    room_messages = Message.objects.all()[:3]
    context = {'activities':room_messages}
    return render(request, 'base/activity.html', context)
    