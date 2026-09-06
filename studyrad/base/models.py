from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Topic(models.Model):
    # A room is the child of a topic 
    name = models.CharField(max_length=200)
    
    
    def __str__(self):
        return self.name
    
class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic =models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True) #1 room 1 topic
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) #null is for DB, and blank is for a form
    # participants = 
    updated = models.DateTimeField(auto_now=True) #so everytime the save method is called, update this field
    created = models.DateTimeField(auto_now_add=True) #timestamp is created when we first create this instance, so updation in this
    
    
    # So this class contains the meta data, and now this is saying, hey wrt rooms, you order the rooms by first date of updated in desc order and then created in desc order. -updated ==> desc order of updated, only updated ==> asc order
    class Meta: 
        ordering = ['-updated', '-created']
    
    # this function specifies how should the rows be visible inside the table, in admin panel
    def __str__(self):
        return self.name

class Message(models.Model): # 1:n relationship model
    user = models.ForeignKey(User, on_delete=models.CASCADE) #currently using default django model
    room = models.ForeignKey(Room, on_delete=models.CASCADE) #when a room is deleted, delete all msg 
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.body[0:50]
    
    