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
        (u'0', u'Signed Up'),
        (u'1', u'First Login'),
        (u'2', u'Active'),
        (u'3', u'Inactive'),
    )

    user = models.ForeignKey(User, unique=True)
    date_created = models.DateField(auto_now_add=True)
    is_gmail = models.BooleanField(default=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=u'0')


class UserEvent(models.Model):
    def __unicode__(self):
        return u'%s : %s - %s' % (self.user.username, self.type, self.timestamp)

    EVENT_CHOICES = (
        (u'LI', u'Logged in'),
        (u'LO', u'Logged out'),
        (u'IF', u'Info'),
        (u'ER', u'Error'),
        (u'RP', u'Reset Password'),
        (u'WP', u'Wrong Password'),
        (u'04', u'404 Page'),
    )

    user = models.ForeignKey(User)
    type = models.CharField(max_length=2, choices=EVENT_CHOICES, default=u'IF')
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    extra = models.CharField(max_length=128, null=True, blank=True)
    ip = models.CharField(max_length=15, null=True, blank=True)
    referer = models.CharField(max_length=128, null=True, blank=True)
    agent = models.CharField(max_length=256, null=True, blank=True)
