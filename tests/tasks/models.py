from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Meeting(models.Model):
    title = models.CharField(max_length=200)
    time = models.DateTimeField(null=True, blank=True)
    participants = models.ManyToManyField(User, through='Participation', blank=True)


class Participation(models.Model):
    meeting = models.ForeignKey('Meeting', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participations')


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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=3000)
