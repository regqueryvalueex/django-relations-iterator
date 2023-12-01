# django-relations-Iterator

Provides utilities for iterating over django model instances hierarchy

Reasoning and solution for use case with cloning - https://hackernoon.com/the-smart-way-to-clone-django-instances

## Example:
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
## Installation

```shell
pip install django-relations-iterator
```

## Features

### Instance tree

```python
from relations_iterator import ConfigurableRelationTree
```

Collects all related instances from model hierarchy accordingly to the provided config

```python
from pprint import pprint
from django.contrib.auth.models import User
from relations_iterator import ConfigurableRelationTree
from tests.meetings.models import Meeting, Participation, Invitation, Comment 


tom = User.objects.create(username='Tom')
jerry = User.objects.create(username='Jerry')
meeting = Meeting.objects.create(title='dinner')
tom_participation = Participation.objects.create(user_id=tom.id, meeting_id=meeting.id)
jerry_participation = Participation.objects.create(user_id=jerry.id, meeting_id=meeting.id)
Invitation.objects.create(user_id=jerry.id, meeting_id=meeting.id)
Comment.objects.create(user_id=jerry.id, meeting_id=meeting.id)


config = {
    'participations': {
        'invitations': {}
    }
}

meeting = Meeting.objects.last()
tree = ConfigurableRelationTree(root=instance, structure=config)
pprint(tree.tree)
```

```python
# Output:
{
    <TreeNode for Meeting: Meeting object (1)>: {
        <ManyToOneRel: meetings.participation>: {
            <TreeNode for Participation: Participation object (1)>: {
                <ManyToOneRel: meetings.invitation>: {
                    <TreeNode for Invitation: Invitation object (1)>: {}
                }
            },
            <TreeNode for Participation: Participation object (2)>: {
                <ManyToOneRel: meetings.invitation>: {}
            }
        }
    }
}
```

For provided config tree will build himself only with `participations` and `invitations` relations and will ignore any other relations.

### Tree iterator

```python
from relations_iterator import RelationTreeIterator
```

Iterates over provided tree and yieds nodes one by one

For example above it will look like

```python
pprint(list(node for node in RelationTreeIterator(tree)))
```

```python
# Output
[<TreeNode for Meeting: Meeting object (1)>,
 <TreeNode for Participation: Participation object (1)>,
 <TreeNode for Invitation: Invitation object (1)>,
 <TreeNode for Participation: Participation object (2)>]
```

### Abstract Visitor iterator

```python
from relations_iterator import AbstractVisitor
```

Provides abstract class, with interface to implement visitor pattern. You must implement `.visit(node)` method, to complete implementation

#### Examples:
#### Clone visitor

```python
from relations_iterator import TreeNode


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

```

Clone visitor will clone every instance in hierarchy and set proper parent, so it can be used to implement instance hierarchy clone

```python
CLONE_STRUCTURE = {
    'participations': {
        'invitations': {}
    }
}

def clone(instance, config):
    visitor = CloneVisitor()
    tree = ConfigurableRelationTree(root=instance, structure=config)
    for node in RelationTreeIterator(tree=tree):
        visitor.visit(node)

clone(meeting, CLONE_STRUCTURE)

cloned_meeting = Meeting.objects.last()
tree = ConfigurableRelationTree(root=cloned_meeting, structure=CLONE_STRUCTURE)
pprint(tree.tree)
```

```python
# Output
{
    <TreeNode for Meeting: Meeting object (2)>: {
        <ManyToOneRel: meetings.participation>: {
            <TreeNode for Participation: Participation object (3)>: {
                <ManyToOneRel: meetings.invitation>: {
                    <TreeNode for Invitation: Invitation object (2)>: {}
                }
            },
            <TreeNode for Participation: Participation object (3)>: {
                <ManyToOneRel: meetings.invitation>: {}
            }
        }
    }
}
```

#### Path print visitor

Path print visitor will print all parent nodes from root to curent node

```python
class PathPrintVisitor(AbstractVisitor):
    def visit(self, node: TreeNode):
        print(list(reversed(self.get_path(node))))

    def get_path(self, node: TreeNode):
        path = [node]
        if node.parent:
            path.extend(self.get_path(node.parent))
        return path

visitor = PathPrintVisitor()
for node in RelationTreeIterator(tree):
    visitor.visit(node)
```

```python
# Output
[<TreeNode for Meeting: Meeting object (2)>]
[<TreeNode for Meeting: Meeting object (2)>, <TreeNode for Participation: Participation object (3)>]
[<TreeNode for Meeting: Meeting object (2)>, <TreeNode for Participation: Participation object (3)>, <TreeNode for Invitation: Invitation object (2)>]
[<TreeNode for Meeting: Meeting object (2)>, <TreeNode for Participation: Participation object (4)>]
```
