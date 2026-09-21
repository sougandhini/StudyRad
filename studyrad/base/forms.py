from django.forms import ModelForm
from .models import Room, Message

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__' #the form fields will be the DB-editable fields
        

class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body']