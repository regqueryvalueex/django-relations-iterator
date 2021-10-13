import typing

from django.db.models import Model, ManyToManyRel, ManyToOneRel, OneToOneRel

Relation = typing.Union[ManyToManyRel, ManyToOneRel, OneToOneRel]
RelationTree = typing.Dict['TreeNode', typing.Dict[Relation, 'RelationTree']]
RelationTreeConfig = typing.Dict[str, 'RelationTreeConfig']


class TreeNode:
    def __init__(
        self,
        *,
        instance: Model,
        parent: typing.Optional['TreeNode'] = None,
        relation: typing.Optional[Relation] = None
    ):
        self.instance = instance
        self.parent = parent
        self.relation = relation

    @property
    def model_class(self):
        return type(self.instance)

    def __hash__(self):
        return hash(f'{str(self.model_class)}-{self.instance.id}')

    def __repr__(self):
        return f'<{type(self).__name__} for {repr(self.instance).strip("<>")}>'


class ConfigurableRelationTree:
    def __init__(self, *, root: Model, structure: RelationTreeConfig):
        self.root: Model = root
        self.structure: RelationTreeConfig = structure
        self.tree: RelationTree = self.collect()

    def collect(
        self,
        *,
        node: typing.Optional[TreeNode] = None,
        structure: typing.Optional[RelationTreeConfig] = None
    ) -> RelationTree:
        if not node:
            node = self.get_node(instance=self.root)

        root = node.instance
        structure = structure if structure is not None else self.structure
        subtree = {}
        tree = {node: subtree}

        for sub_relation_name, substructure in structure.items():
            sub_relation = root._meta.get_field(sub_relation_name)
            related_instances = self._get_related_instances(instance=root, relation=sub_relation)
            subtree[sub_relation] = {}
            for related_instance in related_instances:
                node = self.get_node(instance=related_instance, relation=sub_relation, parent=node)
                subtree[sub_relation].update(
                    self.collect(node=node, structure=substructure)
                )

        return tree

    def _get_related_instances(
        self,
        *,
        instance: Model,
        relation: Relation
    ) -> typing.List[Model]:
        accessor_name = relation.get_accessor_name()
        if relation.one_to_one:
            instance = getattr(instance, accessor_name, None)
            related_instances = [instance] if instance is not None else []
        else:
            related_instances = list(getattr(instance, accessor_name).all())
        return related_instances

    def get_node(
        self,
        *,
        instance: Model,
        parent: typing.Optional[TreeNode] = None,
        relation: typing.Optional[Relation] = None
    ) -> TreeNode:
        return TreeNode(
            instance=instance,
            parent=parent,
            relation=relation,
        )
