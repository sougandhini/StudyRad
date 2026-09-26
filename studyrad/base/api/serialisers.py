from rest_framework.serializers import ModelSerializer
from base.models import Room

# take model as an object and turn it into a JSON object 

class RoomSerialiser(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
