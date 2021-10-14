from django.conf import settings
from django.db import models


class Meeting(models.Model):
    title = models.CharField(max_length=200)
    time = models.DateTimeField(null=True, blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Participation', blank=True)


class Participation(models.Model):
    meeting = models.ForeignKey('Meeting', on_delete=models.CASCADE, related_name='participations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participations')


class Invitation(models.Model):
    STATUS_SENT = 'sent'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'
    STATUS_CHOICES = (
        (STATUS_SENT, STATUS_SENT),
        (STATUS_ACCEPTED, STATUS_ACCEPTED),
        (STATUS_DECLINED, STATUS_DECLINED),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SENT)
    participation = models.ForeignKey('Participation', on_delete=models.CASCADE, related_name='invitations')


class Comment(models.Model):
    meeting = models.ForeignKey('Meeting', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(max_length=3000)
