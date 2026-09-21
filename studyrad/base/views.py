from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Room, Topic, Message
from .forms import RoomForm
from django.db.models import Count
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

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
            messages.error(request, 'Username or Password does not exist')
    context={'page':page}
    return render(request, 'base/login_register.html', context)

def logout_user(request):
    logout(request) # this method deletes token hence deletes the user
    return redirect('home')
    
def register_user(request):
    form = UserCreationForm
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
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
    topics = Topic.objects.annotate(room_count=Count("room")).order_by('-room_count')
    context = {'rooms': rooms, 'topics':topics, 'room_count':room_count} #this is for passing data to my response
    return render(request, 'base/home.html', context)

# Read
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.messages.all().order_by('-created') #reverse fk used here
    
    
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        # if we dont do this also, the page will work, but problem is the post without any redirect operation may result in some complications
        return redirect('room',pk=room.id)
        
    context = {'room': room, 'room_messages':room_messages}
    return render(request, 'base/room.html', context)

# CRUD ON ROOMS 

# Create Room only if user is logged in
@login_required(login_url='login') #if a user is not logged in then he will be redirected to login
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        
    form = RoomForm()
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

# Update Room

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) #means hey prefill this form with the instance of room
    
    # if a user is not the creater of that room, he should not delete the room
    if request.user != room.host:
        return HttpResponse("You're not authorised to update this room")
        
    if request.method=="POST":
        form = RoomForm(request.POST, instance=room) #if we dont specify the value of instance it just creates a new instance rather than updating the current one
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
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
    return render(request, 'base/delete.html', {'obj':room})


    