import factory
from django.contrib.auth import get_user_model

from meetings.models import Meeting, Participation, Invitation, Comment

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'{n}mail@example.com')

    class Meta:
        model = User


class MeetingFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: f'title_{n}')

    class Meta:
        model = Meeting


class ParticipationFactory(factory.django.DjangoModelFactory):
    meeting = factory.SubFactory(MeetingFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Participation


class InvitationFactory(factory.django.DjangoModelFactory):
    participation = factory.SubFactory(ParticipationFactory)

    class Meta:
        model = Invitation


class CommentFactory(factory.django.DjangoModelFactory):
    meeting = factory.SubFactory(MeetingFactory)
    user = factory.SubFactory(UserFactory)
    description = factory.Sequence(lambda n: f'description_{n}')

    class Meta:
        model = Comment
