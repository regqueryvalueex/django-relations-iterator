from relations_iterator.relation_tree import TreeNode
from relations_iterator.visitor import AbstractVisitor

CLONE_STRUCTURE = {
    'participants': {
        'invitations': {}
    }
}


class CloneVisitor(AbstractVisitor):
    def visit(self, node: TreeNode):
        node.instance.id = None

