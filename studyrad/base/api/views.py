from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serialisers import RoomSerialiser


# creating first view
@api_view(['GET']) #the param value says what does this function do, this only allows get
def getRoute(request):
    routes = [
        'GET /studyrad',
        'GET /studyrad/rooms',
        'GET /studyrad/room/:id'
    ]
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    # this is a query set and its not directly convertible to json response, so we need to serialise it to render it in JSON
    serialiser = RoomSerialiser(rooms, many=True)
    return Response(serialiser.data)

@api_view(['GET'])
def getRoom(request,pk):
    room = Room.objects.get(id=pk)
    serialiser = RoomSerialiser(room)
    return Response(serialiser.data)