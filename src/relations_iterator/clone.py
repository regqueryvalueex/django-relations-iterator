from django.db.models import Model

from . import AbstractVisitor, TreeNode, ConfigurableRelationTree, RelationTreeIterator


class CloneVisitor(AbstractVisitor):
    def visit(self, node: TreeNode):
        node.instance.pk = None
        if node.parent is not None:
            parent_joining_field, instance_joining_field = node.relation.get_joining_fields()[0]
            setattr(
                node.instance,
                instance_joining_field.attname,
                parent_joining_field.value_from_object(node.parent.instance)
            )
        self.customize(node.instance)
        node.instance.save()

    def customize(self, instance: Model) -> None:
        pass


def clone(instance: Model, config: dict, visitor: AbstractVisitor) -> None:
    tree = ConfigurableRelationTree(root=instance, structure=config)
    for node in RelationTreeIterator(tree=tree):
        visitor.visit(node)
