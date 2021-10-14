# django-relations-Iterator

Provides utilities for iterating over django model instances hierarchy

##Example:
#### Simple instances tree clone


```python
#models.py
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

```

```python
#clone.py
from relations_iterator import TreeNode, AbstractVisitor, RelationTreeIterator, ConfigurableRelationTree
from .models import Meeting

# because of config, tree will ignore comments, but will consider all participations and invitations
CLONE_STRUCTURE = {
    'participations': {
        'invitations': {}
    }
}


class CloneVisitor(AbstractVisitor):
    def visit(self, node: TreeNode):
        node.instance.pk = None
        if node.parent is not None:
            parent_joining_column, instance_joining_column = node.relation.get_joining_columns()[0]
            setattr(
                node.instance,
                instance_joining_column,
                getattr(node.parent.instance, parent_joining_column)
            )
        node.instance.save()


def clone(instance, config):
    
    visitor = CloneVisitor()
    tree = ConfigurableRelationTree(root=instance, structure=config)
    for node in RelationTreeIterator(tree=tree):
        visitor.visit(node)

        
meeting = Meeting.objects.last()
clone(meeting, CLONE_STRUCTURE)

```
