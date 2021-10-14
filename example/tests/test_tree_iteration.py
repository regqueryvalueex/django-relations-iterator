import pytest

from relations_iterator.iterator import RelationTreeIterator
from relations_iterator.relation_tree import ConfigurableRelationTree
from meetings.models import Meeting
from .factories import MeetingFactory, ParticipationFactory, InvitationFactory

pytestmark = pytest.mark.django_db


def test_tree_for_one_instance():
    participation = ParticipationFactory()
    config = {}
    tree = ConfigurableRelationTree(root=participation.meeting, structure=config)
    nodes = list(RelationTreeIterator(tree=tree))

    assert len(nodes) == 1
    assert nodes[0].instance == participation.meeting


def test_tree_for_complex_tree():
    config = {
        'participations': {
            'invitations': {}
        }
    }

    meeting1 = MeetingFactory()
    meeting2 = MeetingFactory()

    participation1 = ParticipationFactory(meeting=meeting1)
    participation2 = ParticipationFactory(meeting=meeting1)
    ParticipationFactory(meeting=meeting2)

    invitation = InvitationFactory(participation=participation1)

    tree = ConfigurableRelationTree(root=meeting1, structure=config)

    expected = [
        meeting1,
        participation1,
        invitation,
        participation2,
    ]
    nodes = list(RelationTreeIterator(tree=tree))

    assert len(nodes) == len(expected)
    assert [node.instance for node in nodes] == expected


def test_get_related_instances():
    meeting1 = MeetingFactory()
    meeting2 = MeetingFactory()

    participation1 = ParticipationFactory(meeting=meeting1)
    participation2 = ParticipationFactory(meeting=meeting1)
    participation3 = ParticipationFactory(meeting=meeting2)

    tree1 = ConfigurableRelationTree(root=meeting1, structure={})
    tree2 = ConfigurableRelationTree(root=meeting2, structure={})

    field = Meeting._meta.get_field('participations')

    related_instances1 = tree1._get_related_instances(instance=meeting1, relation=field)
    related_instances2 = tree2._get_related_instances(instance=meeting2, relation=field)

    assert related_instances1 == [participation1, participation2]
    assert related_instances2 == [participation3]
