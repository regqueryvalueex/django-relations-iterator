from relations_iterator.relation_tree import TreeNode
from relations_iterator.visitor import AbstractVisitor

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
