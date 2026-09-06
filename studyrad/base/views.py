from django.shortcuts import render, redirect
from .models import Room, Topic
from .forms import RoomForm
from django.db.models import Count

# Create your views here.

# rooms = [
#     {'id':1, 'name': "Lets learn python!"},
#     {'id':2, 'name': "Lets learn System design!"},
#     {'id':3, 'name': "Learn GO!"}
# ]

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(topic__name__icontains=q) #make sure the value in topic name is present in q
    
    
    # topics = Topic.objects.all() all the topics will be listed, but later change it to those topics which have highest number of rooms
    '''
    SQL: SELECT room.topic FROM room GROUP BY room.topic ORDER BY count(room.id) DESC;
    '''
    topics = Topic.objects.annotate(room_count=Count("room")).order_by('-room_count')
    context = {'rooms': rooms, 'topics':topics} #this is for passing data to my response
    return render(request, 'base/home.html', context)

# Read
def room(request, pk):
    room = Room.objects.get(id=pk)
    context = {'room': room}
    return render(request, 'base/room.html', context)

# CRUD ON ROOMS 

# Create Room
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
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) #means hey prefill this form with the instance of room
    
    if request.method=="POST":
        form = RoomForm(request.POST, instance=room) #if we dont specify the value of instance it just creates a new instance rather than updating the current one
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

# Delete Room
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST': #coz we click on confirm
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})


    