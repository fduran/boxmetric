from django.db import models
from django.contrib.auth.models import User

class Contact(models.Model):
    def __unicode__(self):
        return self.email
    user = models.ForeignKey(User)
    name = models.CharField(max_length=128,null=True,blank=True)
    email = models.EmailField()
    count = models.PositiveIntegerField(null=True,blank=True)
    thumbnail = models.CharField(max_length=128,null=True,blank=True)

class UserProfile(models.Model):
    def __unicode__(self):
        return self.user.username
    user = models.ForeignKey(User, unique=True)
    date_created = models.DateField(auto_now_add=True)
    is_gmail = models.BooleanField(default=True)
