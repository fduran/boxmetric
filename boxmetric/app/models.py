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

    STATUS_CHOICES = (
        (u'0', u'First Login'),
        (u'1', u'Active'),
        (u'2', u'Inactive'),
    )

    user = models.ForeignKey(User, unique=True)
    date_created = models.DateField(auto_now_add=True)
    is_gmail = models.BooleanField(default=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=u'0')
