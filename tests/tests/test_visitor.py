import pytest

from meetings.clone import CloneVisitor
from src.relations_iterator.iterator import RelationTreeIterator
from src.relations_iterator.relation_tree import ConfigurableRelationTree
from meetings.models import Meeting
from .factories import MeetingFactory, ParticipationFactory, InvitationFactory, CommentFactory

pytestmark = pytest.mark.django_db


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
    CommentFactory(meeting=meeting)
    original_meeting_id = meeting.id

    tree = ConfigurableRelationTree(root=meeting, structure=config)

    assert Meeting.objects.count() == 1

    visitor = CloneVisitor()
    for node in RelationTreeIterator(tree=tree):
        visitor.visit(node)

    assert Meeting.objects.count() == 2
    original_meeting = Meeting.objects.get(id=original_meeting_id)
    cloned_meeting = Meeting.objects.exclude(id=original_meeting_id).get()
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
