import pytest
from functools import singledispatchmethod

from meetings.models import Meeting
from relations_iterator.clone import CloneVisitor, clone
from .factories import MeetingFactory, ParticipationFactory, InvitationFactory

pytestmark = pytest.mark.django_db


class CustomCloneVisitor(CloneVisitor):
    @singledispatchmethod
    def customize(self, instance):
        pass

    @customize.register
    def _(self, instance: Meeting):
        instance.title = f'{instance.title}-COPY'
        instance.time = None


def test_clone_visitor():
    config = {
        'participations': {
            'invitations': {}
        }
    }

    meeting = MeetingFactory()
    participation1 = ParticipationFactory(meeting=meeting)
    ParticipationFactory(meeting=meeting)
    InvitationFactory(participation=participation1)
    original_meeting_id = meeting.id

    assert Meeting.objects.count() == 1

    clone(meeting, config, visitor=CustomCloneVisitor())

    assert Meeting.objects.count() == 2
    original_meeting = Meeting.objects.get(id=original_meeting_id)
    cloned_meeting = Meeting.objects.exclude(id=original_meeting_id).get()
    assert cloned_meeting.title == f'{original_meeting.title}-COPY'
    assert cloned_meeting.pk != original_meeting.pk
    assert cloned_meeting.participations.count() == 2
    assert (
            list(cloned_meeting.participations.values_list('user_id', flat=True)) ==
            list(original_meeting.participations.values_list('user_id', flat=True))
    )
    original_participation1 = original_meeting.participations.first()
    cloned_participation1 = cloned_meeting.participations.first()

    assert cloned_participation1.invitations.exists()
    assert (
            list(cloned_participation1.invitations.values_list('id', flat=True)) !=
            list(original_participation1.invitations.values_list('id', flat=True))
    )
    assert not cloned_meeting.comments.exists()
